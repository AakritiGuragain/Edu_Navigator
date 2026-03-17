"""
College Logo Fetcher
--------------------
Visits each college's website, finds their logo, and downloads it.
Saves logos into a ./logos/ folder.

Requirements:
    pip install requests beautifulsoup4 Pillow

Usage:
    python fetch_logos.py
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

# ── College list with known websites ──────────────────────────────────────────
COLLEGES = [
    {"name": "Tribhuvan University",                        "url": "https://tribhuvan-university.edu.np"},
    {"name": "IOE Thapathali Campus",                       "url": "https://ioe.edu.np"},
    {"name": "Pulchowk Campus (TU-IOE)",                    "url": "https://pcampus.edu.np"},
    {"name": "Prithvi Narayan Campus",                      "url": "https://pncampus.edu.np"},
    {"name": "Kathmandu University",                        "url": "https://ku.edu.np"},
    {"name": "KU School of Management (KUSOM)",             "url": "https://kusom.edu.np"},
    {"name": "Pokhara University",                          "url": "https://pu.edu.np"},
    {"name": "Shankar Dev Campus",                          "url": "https://shankerdevcampus.edu.np"},
    {"name": "The British College",                         "url": "https://thebritishcollege.edu.np"},
    {"name": "Softwarica College",                          "url": "https://softwarica.edu.np"},
    {"name": "Islington College",                           "url": "https://islington.edu.np"},
    {"name": "Herald College Kathmandu",                    "url": "https://heraldcollege.edu.np"},
    {"name": "King's College",                              "url": "https://kingscollege.edu.np"},
    {"name": "Nepal Engineering College (NEC)",             "url": "https://nec.edu.np"},
    {"name": "Prime College",                               "url": "https://primecollege.edu.np"},
    {"name": "PAHS – Patan Academy of Health Sciences",     "url": "https://pahs.edu.np"},
    {"name": "Purbanchal University",                       "url": "https://purbanchaluniversity.edu.np"},
    {"name": "Kathford International College",              "url": "https://kathford.edu.np"},
    {"name": "Apex College",                                "url": "https://apexcollege.edu.np"},
    {"name": "TU Teaching Hospital (IOM)",                  "url": "https://iom.edu.np"},
]

OUTPUT_DIR = Path("logos")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Image extensions we accept
IMG_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}

# Keywords that suggest a logo image (checked against src/alt/class/id)
LOGO_KEYWORDS = ["logo", "brand", "emblem", "crest", "seal", "header-img", "site-logo"]


def safe_filename(name: str) -> str:
    return re.sub(r'[^\w\-]', '_', name).strip('_')


def score_img(tag, base_url: str) -> tuple[int, str]:
    """Return (score, absolute_src) for an <img> tag. Higher = more likely a logo."""
    src = tag.get("src") or tag.get("data-src") or ""
    if not src:
        return 0, ""

    abs_src = urljoin(base_url, src)
    src_lower = src.lower()
    alt_lower = (tag.get("alt") or "").lower()
    cls_lower = " ".join(tag.get("class") or []).lower()
    id_lower  = (tag.get("id") or "").lower()
    combined  = src_lower + alt_lower + cls_lower + id_lower

    # Must be a valid image extension
    path_ext = Path(urlparse(src).path).suffix.lower()
    if path_ext not in IMG_EXTS and "?" not in src:
        return 0, ""

    score = 0

    # Strong signals
    for kw in LOGO_KEYWORDS:
        if kw in combined:
            score += 10

    # Logos are usually small-ish (width/height hints)
    w = tag.get("width") or ""
    h = tag.get("height") or ""
    try:
        if 20 <= int(str(w).replace("px","")) <= 400:
            score += 3
    except:
        pass
    try:
        if 20 <= int(str(h).replace("px","")) <= 200:
            score += 3
    except:
        pass

    # SVG and PNG preferred (transparent backgrounds)
    if path_ext in (".svg", ".png"):
        score += 2

    # Penalty: likely a banner/hero/background
    for bad in ["banner", "hero", "slide", "carousel", "bg", "background", "photo", "student"]:
        if bad in combined:
            score -= 5

    return score, abs_src


def fetch_logo(college: dict) -> str | None:
    name = college["name"]
    url  = college["url"]
    fname = safe_filename(name)

    print(f"\n{'─'*60}")
    print(f"🔍  {name}")
    print(f"    {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"    ❌  Could not reach site: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # ── Strategy 1: score all <img> tags ──────────────────────────────────────
    candidates = []
    for img in soup.find_all("img"):
        score, abs_src = score_img(img, url)
        if score > 0:
            candidates.append((score, abs_src))

    # ── Strategy 2: look inside common logo containers ────────────────────────
    logo_containers = soup.select(
        "header img, .logo img, .site-logo img, #logo img, "
        ".navbar-brand img, .navbar img, nav img, "
        "[class*='logo'] img, [id*='logo'] img"
    )
    for img in logo_containers:
        score, abs_src = score_img(img, url)
        if abs_src:
            candidates.append((score + 15, abs_src))   # boost for being in a logo container

    # ── Strategy 3: <link rel="icon"> as last resort ──────────────────────────
    favicon_src = None
    for link in soup.find_all("link", rel=lambda r: r and any(x in r for x in ["icon", "apple-touch-icon"])):
        href = link.get("href")
        if href:
            favicon_src = urljoin(url, href)

    if not candidates:
        if favicon_src:
            print(f"    ⚠️  No logo found, falling back to favicon")
            candidates.append((1, favicon_src))
        else:
            print(f"    ❌  No image candidates found")
            return None

    # Pick highest-scored candidate
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_score, best_src = candidates[0]
    print(f"    ✅  Best candidate (score={best_score}): {best_src}")

    # ── Download the image ────────────────────────────────────────────────────
    try:
        img_resp = requests.get(best_src, headers=HEADERS, timeout=15)
        img_resp.raise_for_status()

        ext = Path(urlparse(best_src).path).suffix.lower() or ".png"
        if ext not in IMG_EXTS:
            ext = ".png"

        out_path = OUTPUT_DIR / f"{fname}{ext}"
        out_path.write_bytes(img_resp.content)
        size_kb = len(img_resp.content) // 1024
        print(f"    💾  Saved → {out_path}  ({size_kb} KB)")
        return str(out_path)

    except Exception as e:
        print(f"    ❌  Failed to download image: {e}")
        return None


def main():
    print("=" * 60)
    print("  College Logo Fetcher")
    print("=" * 60)

    results = {}
    for college in COLLEGES:
        path = fetch_logo(college)
        results[college["name"]] = path
        time.sleep(1.2)   # polite delay between requests

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    success = [k for k, v in results.items() if v]
    failed  = [k for k, v in results.items() if not v]

    print(f"\n✅  Downloaded ({len(success)}/{len(COLLEGES)}):")
    for name in success:
        print(f"    • {name}")

    if failed:
        print(f"\n❌  Failed ({len(failed)}):")
        for name in failed:
            print(f"    • {name}")
        print(f"\n💡  For failed ones, manually download from their websites")
        print(f"    and save to the logos/ folder with the naming pattern:")
        print(f"    College_Name.png")

    print(f"\n📁  All logos saved in: ./{OUTPUT_DIR}/")
    print("\nDone!")


if __name__ == "__main__":
    main()
