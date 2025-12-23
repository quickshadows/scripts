#!/usr/bin/env python3
import argparse
import concurrent.futures as cf
import datetime as dt
import logging
import math
import os
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple

import boto3
from botocore.config import Config as BotoConfig
from getpass import getpass

from dotenv import find_dotenv, load_dotenv, set_key  # pip install python-dotenv


def ensure_env(logger=None, dotenv_path: str = ".env"):
    """
    1) Загружает .env если есть
    2) Если обязательных параметров нет — спрашивает и сохраняет в .env
    3) Кладёт значения в os.environ, чтобы они были доступны в текущем запуске
    """
    # find_dotenv() ищет .env выше по дереву; если не найден — вернёт пустую строку. [web:75]
    found = find_dotenv(dotenv_path, usecwd=True) or dotenv_path

    # Важно: load_dotenv по умолчанию НЕ перетирает уже заданные переменные окружения. [web:75]
    load_dotenv(found, override=False)

    def have(k: str) -> bool:
        v = os.getenv(k)
        return v is not None and str(v).strip() != ""

    def ask(k: str, prompt: str, secret: bool = False, default: str = "") -> str:
        if have(k):
            return os.getenv(k)  # уже есть — не спрашиваем

        p = prompt
        if default:
            p += f" (default: {default})"
        p += ": "

        val = getpass(p) if secret else input(p)
        val = val.strip()
        if not val and default:
            val = default

        if not val:
            raise SystemExit(f"Missing required value for {k}")

        # set_key пишет в .env, но не обновляет os.environ автоматически в этом же процессе. [web:77][web:92]
        set_key(found, k, val)
        os.environ[k] = val
        if logger:
            logger.info(f"Saved {k} to {found}")
        return val

    # --- обязательные для не-AWS S3 (как у вас) ---
    ask("S3_ENDPOINT_URL", "S3 endpoint URL, e.g. https://storage.example.com", secret=False)

    # region лучше иметь всегда (для AWS обязателен, для S3-compatible часто тоже нужен). [web:24]
    ask("AWS_DEFAULT_REGION", "AWS region / S3 region name", secret=False, default="ru-1")

    # addressing style: path/virtual/auto (для многих S3-compatible нужен path). [web:47]
    ask("S3_ADDRESSING_STYLE", "S3 addressing style (path|virtual|auto)", secret=False, default="path")

    # --- креды (если вы НЕ используете AWS_PROFILE) ---
    # Если планируете пользоваться профилями awscli, эти 2 строки можно не заполнять. [web:21]
    ask("AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID", secret=False)
    ask("AWS_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY", secret=True)

    # Session token опционален (только для временных кредов)
    if not have("AWS_SESSION_TOKEN"):
        token = input("AWS_SESSION_TOKEN (optional, press Enter to skip): ").strip()
        if token:
            set_key(found, "AWS_SESSION_TOKEN", token)
            os.environ["AWS_SESSION_TOKEN"] = token
            if logger:
                logger.info(f"Saved AWS_SESSION_TOKEN to {found}")

    return found


# ----------------------------
# Logging
# ----------------------------
def setup_logger(log_file: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("s3-loadtest")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    fmt = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03dZ %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Ensure single set of handlers
    if not logger.handlers:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        logger.addHandler(sh)

        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


# ----------------------------
# Rate limiting (token bucket)
# ----------------------------
class TokenBucket:
    """
    Thread-safe token bucket limiter for bytes/sec.
    If rate_bytes_per_sec is None or 0 => unlimited.
    """
    def __init__(self, rate_bytes_per_sec: Optional[float]):
        self.rate = float(rate_bytes_per_sec or 0.0)
        self.capacity = self.rate if self.rate > 0 else 0.0
        self.tokens = self.capacity
        self.updated = time.monotonic()
        self.lock = threading.Lock()

    def acquire(self, nbytes: int):
        if self.rate <= 0:
            return

        need = float(nbytes)
        while True:
            with self.lock:
                now = time.monotonic()
                elapsed = now - self.updated
                self.updated = now

                # Refill
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

                if self.tokens >= need:
                    self.tokens -= need
                    return

                missing = need - self.tokens
                sleep_s = missing / self.rate if self.rate > 0 else 0.0

            if sleep_s > 0:
                time.sleep(sleep_s)
            else:
                time.sleep(0)


# ----------------------------
# Generated stream (no disk)
# ----------------------------
class GeneratedStream:
    """
    File-like object that generates bytes on the fly up to total_size.
    It also throttles reads using a TokenBucket.
    """
    def __init__(self, total_size: int, limiter: TokenBucket, chunk_size: int, pattern: bytes = b"\0"):
        self.remaining = int(total_size)
        self.limiter = limiter
        self.chunk_size = int(chunk_size)
        self.pattern = pattern if pattern else b"\0"
        self._lock = threading.Lock()

    def read(self, n: int = -1) -> bytes:
        with self._lock:
            if self.remaining <= 0:
                return b""
            if n is None or n < 0:
                n = self.chunk_size
            n = min(n, self.chunk_size, self.remaining)

            self.limiter.acquire(n)
            self.remaining -= n

        # Produce bytes (avoid huge allocations beyond chunk_size)
        if len(self.pattern) == 1:
            return self.pattern * n
        # Repeat pattern if longer
        reps = (n + len(self.pattern) - 1) // len(self.pattern)
        return (self.pattern * reps)[:n]


# ----------------------------
# Helpers
# ----------------------------
def mbps_to_bytes_per_sec(mbps: float) -> float:
    # Mbps = megabits/sec; bytes/sec = (Mbps * 1024*1024) / 8
    return (float(mbps) * 1024 * 1024) / 8.0


def human_bytes(n: float) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    x = float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            return f"{x:.2f} {u}"
        x /= 1024.0
    return f"{x:.2f} B"


def now_tag() -> str:
    return dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


# ----------------------------
# Multipart upload
# ----------------------------
def multipart_upload_object(
    s3,
    logger: logging.Logger,
    bucket: str,
    key: str,
    total_size: int,
    part_size: int,
    upload_limiter: TokenBucket,
    io_chunk_size: int,
    parallel_parts: int,
    extra_args: Optional[dict] = None,
) -> Dict:
    """
    Upload an object using explicit multipart upload.
    Returns dict with timings and stats.
    """
    extra_args = extra_args or {}
    parts_count = int(math.ceil(total_size / part_size))
    logger.info(f"UPLOAD start bucket={bucket} key={key} size={total_size}B parts={parts_count} part_size={part_size}B parallel_parts={parallel_parts}")

    t0 = time.monotonic()
    resp = s3.create_multipart_upload(Bucket=bucket, Key=key, **extra_args)
    upload_id = resp["UploadId"]

    etags: Dict[int, str] = {}
    uploaded_bytes = 0
    uploaded_lock = threading.Lock()
    last_log_t = time.monotonic()

    def upload_one_part(part_number: int) -> Tuple[int, str, int, float]:
        start = (part_number - 1) * part_size
        this_size = min(part_size, total_size - start)

        body = GeneratedStream(total_size=this_size, limiter=upload_limiter, chunk_size=io_chunk_size)
        pt0 = time.monotonic()
        r = s3.upload_part(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
            PartNumber=part_number,
            Body=body,
        )
        pt1 = time.monotonic()
        return part_number, r["ETag"], this_size, (pt1 - pt0)

    try:
        if parallel_parts <= 1:
            for pn in range(1, parts_count + 1):
                part_number, etag, this_size, dt_s = upload_one_part(pn)
                etags[part_number] = etag
                uploaded_bytes += this_size

                # periodic log
                nonlocal_last = time.monotonic()
                if nonlocal_last - last_log_t >= 2.0:
                    rate = uploaded_bytes / max(0.001, (nonlocal_last - t0))
                    logger.info(f"UPLOAD progress key={key} uploaded={uploaded_bytes}B/{total_size}B avg_rate={human_bytes(rate)}/s")
                    last_log_t = nonlocal_last
        else:
            with cf.ThreadPoolExecutor(max_workers=parallel_parts) as ex:
                futs = [ex.submit(upload_one_part, pn) for pn in range(1, parts_count + 1)]
                for fut in cf.as_completed(futs):
                    part_number, etag, this_size, dt_s = fut.result()
                    etags[part_number] = etag
                    with uploaded_lock:
                        uploaded_bytes_local = sum(
                            min(part_size, total_size - (pn - 1) * part_size)
                            for pn in etags.keys()
                        )
                    nonlocal_last = time.monotonic()
                    if nonlocal_last - last_log_t >= 2.0:
                        rate = uploaded_bytes_local / max(0.001, (nonlocal_last - t0))
                        logger.info(f"UPLOAD progress key={key} uploaded={uploaded_bytes_local}B/{total_size}B avg_rate={human_bytes(rate)}/s")
                        last_log_t = nonlocal_last

        # Complete
        parts_payload = [{"ETag": etags[pn], "PartNumber": pn} for pn in sorted(etags.keys())]
        s3.complete_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts_payload},
        )

        t1 = time.monotonic()
        elapsed = t1 - t0
        avg_rate = total_size / max(0.001, elapsed)
        logger.info(f"UPLOAD done bucket={bucket} key={key} elapsed_s={elapsed:.3f} avg_rate={human_bytes(avg_rate)}/s")
        return {"key": key, "size": total_size, "elapsed_s": elapsed, "avg_rate_Bps": avg_rate, "parts": parts_count}

    except Exception as e:
        logger.error(f"UPLOAD error bucket={bucket} key={key} err={repr(e)}; aborting multipart upload")
        try:
            s3.abort_multipart_upload(Bucket=bucket, Key=key, UploadId=upload_id)
        except Exception as e2:
            logger.error(f"UPLOAD abort failed bucket={bucket} key={key} err={repr(e2)}")
        raise


# ----------------------------
# Download (streaming) + cycles
# ----------------------------
def download_object_streaming(
    s3,
    logger: logging.Logger,
    bucket: str,
    key: str,
    download_limiter: TokenBucket,
    read_chunk_size: int,
    log_every_s: float,
) -> Dict:
    logger.info(f"DOWNLOAD start bucket={bucket} key={key} chunk={read_chunk_size}B")

    # HEAD for size (optional, for nicer logs)
    try:
        head = s3.head_object(Bucket=bucket, Key=key)
        total_size = int(head.get("ContentLength", 0))
    except Exception:
        total_size = 0

    t0 = time.monotonic()
    resp = s3.get_object(Bucket=bucket, Key=key)
    body = resp["Body"]

    downloaded = 0
    last_log = time.monotonic()

    while True:
        chunk = body.read(read_chunk_size)
        if not chunk:
            break
        n = len(chunk)
        download_limiter.acquire(n)
        downloaded += n

        now = time.monotonic()
        if now - last_log >= log_every_s:
            rate = downloaded / max(0.001, (now - t0))
            if total_size > 0:
                logger.info(f"DOWNLOAD progress key={key} downloaded={downloaded}B/{total_size}B avg_rate={human_bytes(rate)}/s")
            else:
                logger.info(f"DOWNLOAD progress key={key} downloaded={downloaded}B avg_rate={human_bytes(rate)}/s")
            last_log = now

    t1 = time.monotonic()
    elapsed = t1 - t0
    avg_rate = downloaded / max(0.001, elapsed)
    logger.info(f"DOWNLOAD done bucket={bucket} key={key} bytes={downloaded} elapsed_s={elapsed:.3f} avg_rate={human_bytes(avg_rate)}/s")
    return {"key": key, "downloaded": downloaded, "elapsed_s": elapsed, "avg_rate_Bps": avg_rate}


# ----------------------------
# Main
# ----------------------------
def parse_args():
    p = argparse.ArgumentParser(description="S3 upload/download load test with throttling and full logging.")
    p.add_argument("--bucket", required=True, help="S3 bucket name")
    p.add_argument("--prefix", default="loadtest/", help="Key prefix in bucket")
    p.add_argument("--region", default=None, help="AWS region (optional)")
    p.add_argument("--endpoint-url", default=None, help="Custom S3 endpoint URL (optional)")

    p.add_argument("--sizes-gb", default="1,10,100", help="Comma-separated sizes in GB (default: 1,10,100)")
    p.add_argument("--files-per-size", type=int, default=1, help="How many objects to create per size")

    p.add_argument("--part-size-mb", type=int, default=64, help="Multipart part size in MiB (>= 5). Default 64.")
    p.add_argument("--upload-mbps", type=float, default=0.0, help="Upload speed limit in Mbps (0 = unlimited)")
    p.add_argument("--download-mbps", type=float, default=0.0, help="Download speed limit in Mbps (0 = unlimited)")

    p.add_argument("--parallel-parts", type=int, default=1, help="Upload parts in parallel (threads). Default 1.")
    p.add_argument("--io-chunk-mb", type=int, default=8, help="Internal stream read chunk size in MiB. Default 8.")
    p.add_argument("--download-chunk-mb", type=int, default=8, help="Download read chunk size in MiB. Default 8.")
    p.add_argument("--download-cycles", type=int, default=3, help="How many download cycles per uploaded object")

    p.add_argument("--log-file", default=f"s3_load_test_{now_tag()}.log", help="Log file path")
    p.add_argument("--log-level", default="INFO", help="DEBUG/INFO/WARNING/ERROR")

    p.add_argument("--s3-addressing-style", default="auto", choices=["auto", "path", "virtual"], help="S3 addressing style")
    return p.parse_args()


def main():
    args = parse_args()
    logger = setup_logger(args.log_file, args.log_level)

    dotenv_used = ensure_env(logger=logger)
    logger.info(f"Using dotenv file: {dotenv_used}")

    # Validate
    part_size = args.part_size_mb * 1024 * 1024
    if part_size < 5 * 1024 * 1024:
        raise SystemExit("--part-size-mb must be >= 5 (S3 multipart minimum part size is 5 MiB except last).")

    sizes_gb = [int(x.strip()) for x in args.sizes_gb.split(",") if x.strip()]
    sizes_bytes = [gb * 1024**3 for gb in sizes_gb]

    upload_rate = mbps_to_bytes_per_sec(args.upload_mbps) if args.upload_mbps and args.upload_mbps > 0 else 0.0
    download_rate = mbps_to_bytes_per_sec(args.download_mbps) if args.download_mbps and args.download_mbps > 0 else 0.0
    upload_limiter = TokenBucket(upload_rate)
    download_limiter = TokenBucket(download_rate)

    logger.info(
        f"CONFIG bucket={args.bucket} prefix={args.prefix} region={args.region} endpoint_url={args.endpoint_url} "
        f"sizes_gb={sizes_gb} files_per_size={args.files_per_size} part_size={part_size}B "
        f"upload_mbps={args.upload_mbps} download_mbps={args.download_mbps} parallel_parts={args.parallel_parts}"
    )

    boto_cfg = BotoConfig(
        retries={"max_attempts": 10, "mode": "standard"},
        s3={"addressing_style": args.s3_addressing_style},
    )

    s3 = boto3.client(
        "s3",
        region_name=args.region,
        endpoint_url=args.endpoint_url,
        config=boto_cfg,
    )

    uploaded_keys: List[Tuple[str, int]] = []

    # Upload phase
    for size_b in sizes_bytes:
        for i in range(args.files_per_size):
            key = f"{args.prefix.rstrip('/')}/test_{size_b // (1024**3)}GB_{now_tag()}_{i:02d}.bin"
            multipart_upload_object(
                s3=s3,
                logger=logger,
                bucket=args.bucket,
                key=key,
                total_size=size_b,
                part_size=part_size,
                upload_limiter=upload_limiter,
                io_chunk_size=args.io_chunk_mb * 1024 * 1024,
                parallel_parts=args.parallel_parts,
                extra_args={},  # e.g. {"ServerSideEncryption": "AES256"}
            )
            uploaded_keys.append((key, size_b))

    # Download phase (cycles)
    for key, size_b in uploaded_keys:
        for cycle in range(1, args.download_cycles + 1):
            logger.info(f"DOWNLOAD cycle_start key={key} cycle={cycle}/{args.download_cycles}")
            download_object_streaming(
                s3=s3,
                logger=logger,
                bucket=args.bucket,
                key=key,
                download_limiter=download_limiter,
                read_chunk_size=args.download_chunk_mb * 1024 * 1024,
                log_every_s=2.0,
            )

    logger.info("DONE")


if __name__ == "__main__":
    main()

""" 
python3 s3_load_test.py \
  --bucket 31d5eb06-test-download \
  --prefix loadtest/ \
  --sizes-gb 1,10,100 \
  --files-per-size 1 \
  --part-size-mb 64 \
  --parallel-parts 4 \
  --upload-mbps 1000 \
  --download-mbps 1000 \
  --download-cycles 5 \
  --log-file ./s3_load_test.log \
  --log-level INFO
 """
