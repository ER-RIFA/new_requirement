"""
Download sample video for the tracking pipeline.
Uses yt-dlp with browser impersonation to bypass Cloudflare.

Usage:
    python download_video.py
"""

import subprocess
import sys
import os

OUTPUT_FILE = "input_video.mp4"

# Pexels football video
VIDEO_URL = "https://www.pexels.com/video/men-playing-football-11474931/"


def pip_install(pkg):
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", pkg],
        capture_output=True
    )


def ensure_deps():
    """Install yt-dlp and curl_cffi for Cloudflare bypass."""
    for pkg in ["yt-dlp", "curl_cffi"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"[*] Installing {pkg}...")
            pip_install(pkg)
            print(f"[+] {pkg} installed")


def try_ytdlp():
    """Download using yt-dlp with browser impersonation."""
    try:
        import yt_dlp
        ydl_opts = {
            "format": "best[height<=1080][ext=mp4]/best[ext=mp4]/best",
            "outtmpl": OUTPUT_FILE,
            "quiet": False,
            "impersonate": "chrome",
        }
        print(f"\n[*] Attempting yt-dlp with Chrome impersonation...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([VIDEO_URL])
        return os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 1_000_000
    except Exception as e:
        print(f"[!] yt-dlp failed: {e}")
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        return False


def try_powershell():
    """Download using PowerShell Invoke-WebRequest with browser user-agent."""
    print("\n[*] Attempting PowerShell download from Pexels CDN...")

    # try several CDN URL patterns
    cdn_urls = [
        f"https://videos.pexels.com/video-files/11474931/11474931-hd_1920_1080_30fps.mp4",
        f"https://videos.pexels.com/video-files/11474931/11474931-hd_1920_1080_25fps.mp4",
        f"https://videos.pexels.com/video-files/11474931/11474931-uhd_2560_1440_30fps.mp4",
        f"https://videos.pexels.com/video-files/11474931/11474931-hd_1280_720_25fps.mp4",
    ]

    for url in cdn_urls:
        print(f"  Trying: {url.split('/')[-1]}")
        ps_cmd = (
            f'$ProgressPreference = "SilentlyContinue"; '
            f'try {{ '
            f'Invoke-WebRequest -Uri "{url}" '
            f'-OutFile "{OUTPUT_FILE}" '
            f'-Headers @{{"User-Agent"="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"; "Referer"="https://www.pexels.com/"}} '
            f'-ErrorAction Stop; '
            f'Write-Host "OK" '
            f'}} catch {{ Write-Host "FAIL: $_" }}'
        )
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout.strip()
        if "OK" in output and os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 1_000_000:
            size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
            print(f"[+] Downloaded! ({size_mb:.1f} MB)")
            return True
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

    return False


def try_curl():
    """Download using curl (ships with Windows 10+)."""
    print("\n[*] Attempting curl download...")

    cdn_urls = [
        f"https://videos.pexels.com/video-files/11474931/11474931-hd_1920_1080_30fps.mp4",
        f"https://videos.pexels.com/video-files/11474931/11474931-hd_1920_1080_25fps.mp4",
        f"https://videos.pexels.com/video-files/11474931/11474931-hd_1280_720_25fps.mp4",
    ]

    for url in cdn_urls:
        print(f"  Trying: {url.split('/')[-1]}")
        try:
            result = subprocess.run(
                [
                    "curl", "-L", "-o", OUTPUT_FILE,
                    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "-H", "Referer: https://www.pexels.com/",
                    "--fail", "--silent", "--show-error",
                    url,
                ],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0 and os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 1_000_000:
                size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
                print(f"[+] Downloaded! ({size_mb:.1f} MB)")
                return True
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
        except FileNotFoundError:
            print("  curl not found, skipping...")
            return False
        except Exception as e:
            print(f"  Failed: {e}")
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)

    return False


def main():
    # skip if already downloaded
    if os.path.exists(OUTPUT_FILE):
        size = os.path.getsize(OUTPUT_FILE)
        if size > 5 * 1024 * 1024:
            print(f"[*] '{OUTPUT_FILE}' exists ({size // (1024*1024)} MB), ready to use.")
            return
        else:
            os.remove(OUTPUT_FILE)

    print("=" * 50)
    print("  Downloading sample football video")
    print(f"  Source: {VIDEO_URL}")
    print("=" * 50)

    ensure_deps()

    # method 1: yt-dlp with impersonation
    if try_ytdlp():
        return

    # method 2: PowerShell
    if try_powershell():
        return

    # method 3: curl
    if try_curl():
        return

    # all failed
    print("\n" + "=" * 50)
    print("  AUTO-DOWNLOAD FAILED - MANUAL STEPS:")
    print("=" * 50)
    print()
    print("  1. Open this URL in your browser:")
    print(f"     {VIDEO_URL}")
    print("  2. Click the 'Free Download' button")
    print("  3. Select 'Original' or 'Full HD'")
    print("  4. Save the file as:")
    print(f"     {os.path.abspath(OUTPUT_FILE)}")
    print()
    print("  Then run:  python main.py --input input_video.mp4")


if __name__ == "__main__":
    main()
