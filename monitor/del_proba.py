#!/usr/bin/env python3

import requests
import time


TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6Imd4V1Qyc2VTNGhiQGtIVmg5fVdqIn0.eyJ1c2VyIjoiY20xODYwMSIsInR5cGUiOiJhcGlfa2V5IiwiYXBpX2tleV9pZCI6IjJiYTJlZjkwLTg0M2QtNDFlZC1hMWU4LTU0NTFiYmUxMTBlYSIsImlhdCI6MTc3Njc2ODA0Mn0.qCFs65mLCrAFFjg20XjjpyTOgA_jmdXXyz0Vh8K3cduR8oaUBcy0grLCgteQReVvBftTMyBliA4TlZtLjAwCuN5itDex6cCUDrx_SMshNXaAFc-Xr72TtfeQCOiQa9PCvuFDaOInB8jvg3DRWtDWqW2W6SqXQT38TKMxuOiHIsU56ut8VddXW748io0weRXLG2A4u5dO3a127Zh77L8gyNRTJc_Hfs6Wbtc8xPgrDGDOXscboaBJuDAqVWaQvnvePA3r0hCendKbkEsnTgJGjH_vmY1fKDyc1vJRmrLB70IsmpS08cZnlsdwLYNxBdl3i0AK4Gro9dTltd_VoPpRG938QnnCMyB5BAl84IPdkz5UnOpktpLoSWaDmEU0ynItzs1IUTZVnh0Lkcgim1yMlYfNzMYX8UAIaS92il_xJX7oioPJeLvqCsdKF7twnX7fJmqUCPiq2Rl0S-Grul_j4QcYHCxDXvMivKbAq_RB7w1QXPP3jm58ZLd47YsXU4Dn"
URL = "https://cloud-staging.kube.timeweb.net/api/v1/probes/{}"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

with open("probi") as f:
    ids = [line.strip() for line in f if line.strip()]

for probe_id in ids:
    resp = requests.delete(URL.format(probe_id), headers=headers)

    print(probe_id, resp.status_code, resp.text)
    time.sleep(0.1)
