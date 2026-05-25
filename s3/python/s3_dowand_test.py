#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import concurrent.futures as cf
import datetime as dt
import logging
import math
import os
import sys
import threading
import time
from getpass import getpass
from typing import Dict, List, Optional, Tuple

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, EndpointConnectionError
from botocore.client import Config as BotocoreClientConfig

# pip install python-dotenv
from dotenv import find_dotenv, load_dotenv, set_key


# ----------------------------
# .env bootstrap (interactive)
# ----------------------------
def ensure_env(dotenv_filename: str = ".env", logger: Optional[logging.Logger] = None) -> str:
    dotenv_path = find_dotenv(dotenv_filename, usecwd=True) or os.path.join(os.getcwd(), dotenv_filename)
    load_dotenv(dotenv_path, override=False)

    def have(k: str) -> bool:
        v = os.getenv(k)
        return v is not None and str(v).strip() != ""

    def save(k: str, v: str):
        set_key(dotenv_path, k, v)
        os.environ[k] = v

    def ask(k: str, prompt: str, secret: bool = False, default: Optional[str] = None, optional: bool = False):
        if have(k):
            return

        p = prompt
        if default is not None:
            p += f" (default: {default})"
        p += ": "

        v = getpass(p).strip() if secret else input(p).strip()
        if not v and default is not None:
            v = default

        if not v:
            if optional:
                return
            raise SystemExit(f"Missing required value for {k}")

        save(k, v)
        if logger:
            logger.info(f"Saved {k} to {dotenv_path}")

    # Timeweb Cloud defaults (you can overwrite in .env)
    ask("S3_ENDPOINT_URL", "S3 endpoint URL", default="https://s3.twcstorage.ru")
    ask("AWS_DEFAULT_REGION", "Region", default="ru-1")
    ask("S3_ADDRESSING_STYLE", "S3 addressing style (path|virtual|auto)", default="path")

    # If using AWS_PROFILE, you can avoid storing long-lived keys in .env
    if not have("AWS_PROFILE"):
        ask("AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID")
        ask("AWS_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY", secret=True)
        ask("AWS_SESSION_TOKEN", "AWS_SESSION_TOKEN (optional, press Enter to skip)", optional=True)

    return dotenv_path


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
# Helpers
# ----------------------------
def mbps_to_bytes_per_sec(mbps: float) -> float:
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


def normalize_prefix(prefix: str) -> str:
    # never allow leading slash in key prefix
    p = (prefix or "").strip()
    p = p.strip("/")
    return p


def make_key(prefix: str, name: str) -> str:
    p = normalize_prefix(prefix)
    return f"{p}/{name}" if p else name


# ----------------------------
# Multipart upload (bytes parts)
# ----------------------------
def multipart_upload_object(
    s3,
    logger: logging.Logger,
    bucket: str,
    key: str,
    total_size: int,
    part_size: int,
    upload_limiter: TokenBucket,
    parallel_parts: int,
    io_chunk_size: int,
    extra_args: Optional[dict] = None,
) -> Dict:
    """
    Upload using explicit multipart upload where each part is sent as bytes of exact length.
    This avoids provider issues with streaming bodies and missing/incorrect Content-Length.
    """
    extra_args = extra_args or {}

    if part_size < 5 * 1024 * 1024:
        raise ValueError("part_size must be >= 5 MiB (except last part).")

    parts_count = int(math.ceil(total_size / part_size))
    logger.info(f"UPLOAD start bucket={bucket} key={key} size={total_size}B parts={parts_count} part_size={part_size}B parallel_parts={parallel_parts}")

    t0 = time.monotonic()
    resp = s3.create_multipart_upload(Bucket=bucket, Key=key, **extra_args)
    upload_id = resp["UploadId"]

    etags: Dict[int, str] = {}
    last_log_t = time.monotonic()
    uploaded_parts: Dict[int, int] = {}
    uploaded_lock = threading.Lock()

    # Pre-alloc one chunk pattern to build parts quickly without per-byte operations
    pattern = b"\0" * min(io_chunk_size, part_size)

    def build_part_bytes(size: int) -> bytes:
        # throttle as if we're "producing/sending" bytes
        # done in chunks so limiter works smoothly
        out = bytearray()
        remaining = size
        while remaining > 0:
            take = min(remaining, len(pattern))
            upload_limiter.acquire(take)
            out.extend(pattern[:take])
            remaining -= take
        return bytes(out)

    def upload_one_part(part_number: int) -> Tuple[int, str, int, float]:
        start = (part_number - 1) * part_size
        this_size = min(part_size, total_size - start)

        data = build_part_bytes(this_size)

        pt0 = time.monotonic()
        r = s3.upload_part(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
            PartNumber=part_number,
            Body=data,
        )
        pt1 = time.monotonic()
        return part_number, r["ETag"], this_size, (pt1 - pt0)

    try:
        if parallel_parts <= 1:
            for pn in range(1, parts_count + 1):
                part_number, etag, this_size, _dt_s = upload_one_part(pn)
                etags[part_number] = etag
                uploaded_parts[part_number] = this_size

                now = time.monotonic()
                if now - last_log_t >= 2.0:
                    uploaded = sum(uploaded_parts.values())
                    rate = uploaded / max(0.001, (now - t0))
                    logger.info(f"UPLOAD progress key={key} uploaded={uploaded}B/{total_size}B avg_rate={human_bytes(rate)}/s")
                    last_log_t = now
        else:
            with cf.ThreadPoolExecutor(max_workers=parallel_parts) as ex:
                futs = [ex.submit(upload_one_part, pn) for pn in range(1, parts_count + 1)]
                for fut in cf.as_completed(futs):
                    part_number, etag, this_size, _dt_s = fut.result()
                    etags[part_number] = etag
                    with uploaded_lock:
                        uploaded_parts[part_number] = this_size

                    now = time.monotonic()
                    if now - last_log_t >= 2.0:
                        uploaded = sum(uploaded_parts.values())
                        rate = uploaded / max(0.001, (now - t0))
                        logger.info(f"UPLOAD progress key={key} uploaded={uploaded}B/{total_size}B avg_rate={human_bytes(rate)}/s")
                        last_log_t = now

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
# Args + main
# ----------------------------
def parse_args():
    p = argparse.ArgumentParser(description="S3 upload/download load test with throttling and full logging (.env supported).")
    p.add_argument("--bucket", required=True, help="S3 bucket name")
    p.add_argument("--prefix", default="loadtest/", help="Key prefix in bucket")

    p.add_argument("--sizes-gb", default="1,10,100", help="Comma-separated sizes in GB (default: 1,10,100)")
    p.add_argument("--files-per-size", type=int, default=1, help="How many objects to create per size")

    p.add_argument("--part-size-mb", type=int, default=64, help="Multipart part size in MiB (>= 5). Default 64.")
    p.add_argument("--upload-mbps", type=float, default=0.0, help="Upload speed limit in Mbps (0 = unlimited)")
    p.add_argument("--download-mbps", type=float, default=0.0, help="Download speed limit in Mbps (0 = unlimited)")

    p.add_argument("--parallel-parts", type=int, default=1, help="Upload parts in parallel (threads). Default 1.")
    p.add_argument("--io-chunk-mb", type=int, default=8, help="Internal bytes build chunk size in MiB. Default 8.")
    p.add_argument("--download-chunk-mb", type=int, default=8, help="Download read chunk size in MiB. Default 8.")
    p.add_argument("--download-cycles", type=int, default=3, help="How many download cycles per uploaded object")

    p.add_argument("--log-file", default=f"s3_load_test_{now_tag()}.log", help="Log file path")
    p.add_argument("--log-level", default="INFO", help="DEBUG/INFO/WARNING/ERROR")
    return p.parse_args()


def main():
    args = parse_args()
    logger = setup_logger(args.log_file, args.log_level)

    # Реально включаем debug botocore (будет много строк; лучше писать в файл)
    boto3.set_stream_logger("botocore", level=logging.DEBUG)  # [web:195]
    logging.getLogger("urllib3").setLevel(logging.INFO)       # [web:190]

    dotenv_used = ensure_env(logger=logger)
    logger.info(f"Using dotenv file: {dotenv_used}")

    endpoint_url = os.getenv("S3_ENDPOINT_URL")
    region = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")
    addr_style = os.getenv("S3_ADDRESSING_STYLE", "path")

    part_size = args.part_size_mb * 1024 * 1024
    sizes_gb = [int(x.strip()) for x in args.sizes_gb.split(",") if x.strip()]
    sizes_bytes = [gb * 1024**3 for gb in sizes_gb]

    upload_rate = mbps_to_bytes_per_sec(args.upload_mbps) if args.upload_mbps and args.upload_mbps > 0 else 0.0
    download_rate = mbps_to_bytes_per_sec(args.download_mbps) if args.download_mbps and args.download_mbps > 0 else 0.0
    upload_limiter = TokenBucket(upload_rate)
    download_limiter = TokenBucket(download_rate)

    logger.info(
        f"CONFIG bucket={args.bucket} prefix={args.prefix} endpoint_url={endpoint_url} region={region} "
        f"addr_style={addr_style} sizes_gb={sizes_gb} files_per_size={args.files_per_size} "
        f"part_size={part_size}B upload_mbps={args.upload_mbps} download_mbps={args.download_mbps} parallel_parts={args.parallel_parts}"
    )

    boto_cfg = BotocoreClientConfig(
        signature_version="s3v4",
        retries={"max_attempts": 10, "mode": "standard"},
        s3={"addressing_style": addr_style},
    )
    logger.info(f"CONFIG sigv={boto_cfg.signature_version} addr_style={addr_style} endpoint_url={endpoint_url} region={region}")

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region,
        config=boto_cfg,
    )

    logger.info(f"S3 client endpoint resolved to: {getattr(s3.meta, 'endpoint_url', None)}")

    uploaded_keys: List[Tuple[str, int]] = []

    for size_b in sizes_bytes:
        for i in range(args.files_per_size):
            obj_name = f"test_{size_b // (1024**3)}GB_{now_tag()}_{i:02d}.bin"
            key = make_key(args.prefix, obj_name)

            multipart_upload_object(
                s3=s3,
                logger=logger,
                bucket=args.bucket,
                key=key,
                total_size=size_b,
                part_size=part_size,
                upload_limiter=upload_limiter,
                parallel_parts=args.parallel_parts,
                io_chunk_size=args.io_chunk_mb * 1024 * 1024,
                extra_args={},
            )
            uploaded_keys.append((key, size_b))

    for key, _size_b in uploaded_keys:
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
    try:
        main()
    except EndpointConnectionError as e:
        print(f"EndpointConnectionError: {e}", file=sys.stderr)
        raise
    except ClientError as e:
        print(f"ClientError: {e}", file=sys.stderr)
        raise
