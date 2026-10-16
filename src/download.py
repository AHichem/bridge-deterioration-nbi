import zipfile
from pathlib import Path

import requests


def url_for(year):
    base = "https://www.fhwa.dot.gov/bridge/nbi/"
    for name in [f"{year}hwybronefiledel.zip", f"{year}hwybronlyonefile.zip"]:
        r = requests.head(base + name, headers={"User-Agent": "Mozilla/5.0"},
                          allow_redirects=True, timeout=30)
        if r.status_code == 200:
            return base + name
    raise ValueError(f"{year}: no file found")


def download_year(year, raw_dir):
    raw_dir = Path(raw_dir)
    zip_path = raw_dir / f"{year}.zip"
    txt_path = raw_dir / f"nbi_{year}.txt"

    # 1. Skip if already done
    if txt_path.exists():
        print(f"{year}: already there, skipping")
        return txt_path

    # 2. Download the zip in chunks
    print(f"{year}: downloading...")
    with requests.get(url_for(year), stream=True, timeout=60,
                      headers={"User-Agent": "Mozilla/5.0"}) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    # 3. Unzip: look inside first
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        print(f"{year}: zip contains {names}")
        inner_name = [n for n in names if n.endswith(".txt")][0]
        z.extract(inner_name, raw_dir)

    # 4. Rename to a predictable name, delete the zip
    (raw_dir / inner_name).rename(txt_path)
    zip_path.unlink()

    print(f"{year}: done → {txt_path.name}")
    return txt_path
