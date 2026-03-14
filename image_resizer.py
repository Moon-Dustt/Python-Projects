#!/usr/bin/env python3
"""
Image Resizer Tool
-------------------
Load and resize single or multiple images at once.
Resized images are saved to a new output folder.

Install dependency:
    pip install Pillow

Run it:
    python image_resizer.py
"""

import os
from pathlib import Path
from PIL import Image


# ─── Supported Image Formats ──────────────────────────────────────────────────

SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif"}

# ─── Default Output Folder ────────────────────────────────────────────────────

OUTPUT_FOLDER = "resized_images"


# ─── Core Resize Function ─────────────────────────────────────────────────────

def resize_image(
    input_path: Path,
    output_path: Path,
    width: int,
    height: int,
    keep_aspect: bool = True,
    quality: int = 90,
):
    """
    Resize a single image and save it to the output path.

    Parameters:
        input_path   — path to the original image
        output_path  — where the resized image will be saved
        width        — target width in pixels
        height       — target height in pixels
        keep_aspect  — maintain aspect ratio (avoids stretching)
        quality      — output quality for JPEGs (1-95)
    """
    # Open the image using Pillow
    img = Image.open(input_path)

    original_size = img.size  # (width, height) tuple

    if keep_aspect:
        # thumbnail() resizes while preserving aspect ratio
        # It fits the image within the given (width, height) box
        img.thumbnail((width, height), Image.LANCZOS)
    else:
        # resize() stretches/squishes to exact dimensions
        img = img.resize((width, height), Image.LANCZOS)

    # Make sure the output folder exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save — pass quality only for JPEG formats
    save_kwargs = {}
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True

    img.save(output_path, **save_kwargs)

    return original_size, img.size  # Return before/after sizes


# ─── Single Image Resize ──────────────────────────────────────────────────────

def resize_single(output_folder: Path, width: int, height: int,
                  keep_aspect: bool, quality: int):
    """Handle resizing of a single image file."""

    # Get the file path from user
    raw = input("\n  Enter image file path: ").strip().strip('"')
    input_path = Path(raw)

    # Validate the file exists
    if not input_path.exists():
        print(f"\n  ❌  File not found: {input_path}\n")
        return

    # Validate it's a supported image format
    if input_path.suffix.lower() not in SUPPORTED:
        print(f"\n  ❌  Unsupported format: {input_path.suffix}")
        print(f"  Supported: {', '.join(SUPPORTED)}\n")
        return

    # Build output path — same filename inside the output folder
    output_path = output_folder / input_path.name

    # Avoid overwriting — add a suffix if file already exists
    if output_path.exists():
        stem   = input_path.stem
        suffix = input_path.suffix
        output_path = output_folder / f"{stem}_resized{suffix}"

    print(f"\n  ⏳  Resizing {input_path.name}...")

    try:
        original, new = resize_image(
            input_path, output_path, width, height, keep_aspect, quality
        )
        print(f"\n  ✅  Done!")
        print(f"  Original size : {original[0]} x {original[1]} px")
        print(f"  New size      : {new[0]} x {new[1]} px")
        print(f"  Saved to      : {output_path}\n")

    except Exception as e:
        print(f"\n  ❌  Failed to resize image: {e}\n")


# ─── Batch Image Resize ───────────────────────────────────────────────────────

def resize_batch(output_folder: Path, width: int, height: int,
                 keep_aspect: bool, quality: int):
    """
    Handle resizing of multiple images from a folder.
    Scans the folder for all supported image files and resizes them all.
    """

    # Get the folder path from user
    raw = input("\n  Enter folder path containing images: ").strip().strip('"')
    folder = Path(raw)

    # Validate folder exists
    if not folder.exists() or not folder.is_dir():
        print(f"\n  ❌  Folder not found: {folder}\n")
        return

    # Find all supported image files in the folder
    images = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED
    ]

    if not images:
        print(f"\n  ❌  No supported images found in: {folder}\n")
        return

    print(f"\n  Found {len(images)} image(s). Starting resize...\n")
    print("  " + "-" * 55)

    success = 0
    failed  = 0

    for img_path in images:
        output_path = output_folder / img_path.name

        # Avoid overwriting
        if output_path.exists():
            output_path = output_folder / f"{img_path.stem}_resized{img_path.suffix}"

        try:
            original, new = resize_image(
                img_path, output_path, width, height, keep_aspect, quality
            )
            print(f"  ✅  {img_path.name:<30}  "
                  f"{original[0]}x{original[1]}  →  {new[0]}x{new[1]}")
            success += 1

        except Exception as e:
            print(f"  ❌  {img_path.name:<30}  Error: {e}")
            failed += 1

    # Summary
    print("  " + "-" * 55)
    print(f"\n  ✅  {success} resized successfully")
    if failed:
        print(f"  ❌  {failed} failed")
    print(f"  📁  Saved to: {output_folder.resolve()}\n")


# ─── Preset Sizes ─────────────────────────────────────────────────────────────

PRESETS = {
    "1": ("Thumbnail",        150,  150),
    "2": ("Small",            480,  360),
    "3": ("Medium",           800,  600),
    "4": ("HD (720p)",       1280,  720),
    "5": ("Full HD (1080p)", 1920, 1080),
    "6": ("Profile Picture",  400,  400),
    "7": ("Custom",             0,    0),  # 0 = user will enter manually
}


def choose_size() -> tuple:
    """
    Let user pick from preset sizes or enter a custom size.
    Returns (width, height) as integers.
    """
    print("\n  -- Choose Output Size --\n")
    for key, (label, w, h) in PRESETS.items():
        if key == "7":
            print(f"  {key}.  {label}")
        else:
            print(f"  {key}.  {label:<20}  {w} x {h} px")

    while True:
        choice = input("\n  Choose size (1-7): ").strip()
        if choice not in PRESETS:
            print("  ⚠️  Invalid choice.\n")
            continue

        label, w, h = PRESETS[choice]

        # Custom size — ask user to enter width and height
        if choice == "7":
            w = get_dimension("  Enter width  (px): ")
            h = get_dimension("  Enter height (px): ")

        return w, h


def get_dimension(prompt: str) -> int:
    """Prompt user for a positive pixel dimension."""
    while True:
        try:
            val = int(input(prompt).strip())
            if val > 0:
                return val
            print("  ⚠️  Must be greater than zero.\n")
        except ValueError:
            print("  ⚠️  Enter a valid number.\n")


# ─── Settings ─────────────────────────────────────────────────────────────────

def get_settings() -> tuple:
    """Ask user for aspect ratio and quality settings."""

    # Aspect ratio
    ar = input("\n  Keep aspect ratio? Prevents stretching [Y/n]: ").strip().lower()
    keep_aspect = ar != "n"

    # Quality (only relevant for JPEGs)
    print("\n  Output quality for JPEGs:")
    print("  1.  High   (90) — recommended")
    print("  2.  Medium (75)")
    print("  3.  Low    (60) — smaller file size")
    q_choice = input("  Choose (1-3) [default: 1]: ").strip()

    quality = {"2": 75, "3": 60}.get(q_choice, 90)

    # Output folder
    custom = input(f'\n  Output folder [default: "{OUTPUT_FOLDER}"]: ').strip()
    folder = Path(custom) if custom else Path(OUTPUT_FOLDER)

    return keep_aspect, quality, folder


# ─── Menu ─────────────────────────────────────────────────────────────────────

def show_menu():
    """Display the main menu."""
    print("\n  MENU")
    print("  1.  Resize a single image")
    print("  2.  Resize all images in a folder (batch)")
    print("  0.  Exit")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 50)
    print("      🖼️   IMAGE RESIZER TOOL")
    print("  Powered by Pillow")
    print("=" * 50)

    while True:
        show_menu()
        choice = input("\n  Choose an option (0-2): ").strip()

        if choice == "0":
            print("\n  👋  Goodbye!\n")
            break

        elif choice in ("1", "2"):
            # Get size and settings
            width, height        = choose_size()
            keep_aspect, quality, output_folder = get_settings()

            if choice == "1":
                resize_single(output_folder, width, height, keep_aspect, quality)
            else:
                resize_batch(output_folder, width, height, keep_aspect, quality)

        else:
            print("\n  ⚠️  Invalid choice. Enter 0, 1, or 2.\n")


if __name__ == "__main__":
    main()