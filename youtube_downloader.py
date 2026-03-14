#!/usr/bin/env python3
"""
YouTube Video Downloader
-------------------------
Download YouTube videos by pasting a link.
Supports single videos, audio-only, and playlist downloads.

Install dependencies:
    pip install pytubefix

Run it:
    python youtube_downloader.py
"""

import os
import sys
from pathlib import Path

# pytubefix is a maintained fork of pytube that works with current YouTube
try:
    from pytubefix import YouTube, Playlist
    from pytubefix.cli import on_progress
except ImportError:
    print("\n  ❌  Missing dependency. Run:  pip install pytubefix\n")
    sys.exit(1)


# ─── Default Download Folder ──────────────────────────────────────────────────

DEFAULT_FOLDER = "downloads"


# ─── Progress Bar ─────────────────────────────────────────────────────────────

def progress_bar(stream, chunk, bytes_remaining):
    """
    Display a live download progress bar in the terminal.
    Called automatically by pytubefix during download.
    """
    total   = stream.filesize
    done    = total - bytes_remaining
    percent = int((done / total) * 100)
    filled  = int(percent / 2)           # 50 chars wide bar
    bar     = "█" * filled + "░" * (50 - filled)
    print(f"\r  [{bar}] {percent}%", end="", flush=True)


# ─── Video Info Display ───────────────────────────────────────────────────────

def display_video_info(yt: YouTube):
    """Print details about the video before downloading."""
    duration = f"{yt.length // 60}:{yt.length % 60:02d}"

    print("\n" + "=" * 55)
    print("  🎬  VIDEO INFO")
    print("=" * 55)
    print(f"  Title    : {yt.title}")
    print(f"  Channel  : {yt.author}")
    print(f"  Duration : {duration}")
    print(f"  Views    : {yt.views:,}")
    print("=" * 55 + "\n")


# ─── Stream Selection ─────────────────────────────────────────────────────────

def choose_quality(yt: YouTube) -> tuple:
    """
    Show available video quality options and let the user pick one.
    Returns (stream, label) where stream is the selected pytubefix stream.
    """
    # Get all progressive streams (video + audio combined) sorted by resolution
    streams = yt.streams.filter(progressive=True, file_extension="mp4") \
                         .order_by("resolution") \
                         .desc()

    if not streams:
        print("\n  ⚠️  No downloadable streams found for this video.\n")
        return None, None

    print("  Available qualities:\n")
    options = list(streams)

    for i, stream in enumerate(options, start=1):
        # Convert file size from bytes to MB
        size_mb = f"{stream.filesize / (1024 * 1024):.1f} MB" if stream.filesize else "Unknown size"
        print(f"  {i}.  {stream.resolution:<8}  {size_mb}")

    print()

    while True:
        try:
            choice = int(input("  Choose quality (enter number): ").strip())
            if 1 <= choice <= len(options):
                selected = options[choice - 1]
                return selected, selected.resolution
            print("  ⚠️  Invalid choice.\n")
        except ValueError:
            print("  ⚠️  Enter a valid number.\n")


# ─── Single Video Download ────────────────────────────────────────────────────

def download_video(url: str, folder: Path, audio_only: bool = False):
    """
    Download a single YouTube video or audio track.

    Parameters:
        url        — YouTube video URL
        folder     — folder to save the downloaded file
        audio_only — if True, download audio only (saved as MP3)
    """
    print("\n  ⏳  Loading video info...")

    try:
        # Create YouTube object with progress callback
        yt = YouTube(url, on_progress_callback=progress_bar)

        display_video_info(yt)

        if audio_only:
            # Get the best available audio stream
            stream = yt.streams.filter(only_audio=True).order_by("abr").last()
            if not stream:
                print("\n  ❌  No audio stream found.\n")
                return
            print(f"  Downloading audio: {yt.title}")
        else:
            # Let user pick video quality
            stream, label = choose_quality(yt)
            if not stream:
                return
            print(f"  Downloading ({label}): {yt.title}")

        # Make sure the output folder exists
        folder.mkdir(parents=True, exist_ok=True)

        print(f"\n  📥  Downloading...\n")

        # Download the file
        out_file = stream.download(output_path=str(folder))

        print(f"\n\n  ✅  Download complete!")
        print(f"  📁  Saved to: {out_file}\n")

        # If audio only, rename the file to .mp3
        if audio_only:
            mp3_path = Path(out_file).with_suffix(".mp3")
            os.rename(out_file, mp3_path)
            print(f"  🎵  Audio saved as: {mp3_path}\n")

    except Exception as e:
        print(f"\n\n  ❌  Download failed: {e}\n")
        print("  💡  Make sure the URL is valid and the video is not age-restricted or private.\n")


# ─── Playlist Download ────────────────────────────────────────────────────────

def download_playlist(url: str, folder: Path, audio_only: bool = False):
    """
    Download all videos from a YouTube playlist.

    Parameters:
        url        — YouTube playlist URL
        folder     — base folder; a subfolder named after the playlist is created
        audio_only — download audio only for each video
    """
    print("\n  ⏳  Loading playlist info...")

    try:
        playlist = Playlist(url)

        # Create a subfolder named after the playlist
        safe_title   = "".join(c for c in playlist.title if c.isalnum() or c in " _-")
        playlist_dir = folder / safe_title.strip()
        playlist_dir.mkdir(parents=True, exist_ok=True)

        total = len(playlist.video_urls)

        print(f"\n  📋  Playlist : {playlist.title}")
        print(f"  Videos     : {total}")
        print(f"  Saving to  : {playlist_dir}\n")

        confirm = input("  Start downloading all videos? (y/n): ").strip().lower()
        if confirm != "y":
            print("\n  Cancelled.\n")
            return

        success = 0
        failed  = 0

        for i, video_url in enumerate(playlist.video_urls, start=1):
            try:
                yt = YouTube(video_url, on_progress_callback=progress_bar)
                print(f"\n  [{i}/{total}]  {yt.title}")

                if audio_only:
                    stream = yt.streams.filter(only_audio=True).order_by("abr").last()
                else:
                    # Use highest resolution for playlist downloads
                    stream = yt.streams.filter(
                        progressive=True, file_extension="mp4"
                    ).order_by("resolution").last()

                if not stream:
                    print("  ⚠️  No stream found, skipping.")
                    failed += 1
                    continue

                out_file = stream.download(output_path=str(playlist_dir))
                print(f"\n  ✅  Saved: {Path(out_file).name}")
                success += 1

            except Exception as e:
                print(f"\n  ❌  Failed: {e}")
                failed += 1

        # Summary
        print("\n" + "=" * 50)
        print(f"  ✅  {success} downloaded successfully")
        if failed:
            print(f"  ❌  {failed} failed")
        print(f"  📁  Saved to: {playlist_dir.resolve()}")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n  ❌  Could not load playlist: {e}\n")
        print("  💡  Make sure the playlist is public and the URL is correct.\n")


# ─── Input Helpers ────────────────────────────────────────────────────────────

def get_url(prompt: str) -> str:
    """Prompt user for a URL and do a basic validation check."""
    while True:
        url = input(prompt).strip()
        if url.startswith("http"):
            return url
        print("  ⚠️  Please paste a valid YouTube URL (starts with http).\n")


def get_folder() -> Path:
    """Ask user for download folder or use default."""
    custom = input(f'  Download folder [default: "{DEFAULT_FOLDER}"]: ').strip()
    return Path(custom) if custom else Path(DEFAULT_FOLDER)


# ─── Menu ─────────────────────────────────────────────────────────────────────

def show_menu():
    """Display the main menu."""
    print("\n  MENU")
    print("  1.  Download a video           (MP4)")
    print("  2.  Download audio only        (MP3)")
    print("  3.  Download a full playlist   (MP4)")
    print("  4.  Download playlist audio    (MP3)")
    print("  0.  Exit")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 50)
    print("      📺  YOUTUBE DOWNLOADER")
    print("=" * 50)

    while True:
        show_menu()
        choice = input("\n  Choose an option (0-4): ").strip()

        if choice == "0":
            print("\n  👋  Goodbye!\n")
            break

        elif choice == "1":
            # Download single video
            url    = get_url("\n  Paste YouTube video URL: ")
            folder = get_folder()
            download_video(url, folder, audio_only=False)

        elif choice == "2":
            # Download audio only
            url    = get_url("\n  Paste YouTube video URL: ")
            folder = get_folder()
            download_video(url, folder, audio_only=True)

        elif choice == "3":
            # Download full playlist
            url    = get_url("\n  Paste YouTube playlist URL: ")
            folder = get_folder()
            download_playlist(url, folder, audio_only=False)

        elif choice == "4":
            # Download playlist audio only
            url    = get_url("\n  Paste YouTube playlist URL: ")
            folder = get_folder()
            download_playlist(url, folder, audio_only=True)

        else:
            print("\n  ⚠️  Invalid choice. Enter 0, 1, 2, 3, or 4.\n")


if __name__ == "__main__":
    main()