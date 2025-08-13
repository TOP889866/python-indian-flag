#!/usr/bin/env python3

"""
Python CLI to Create Indian Flag with Your Name
Author: Santhosh Kumar (https://github.com/mskian/python-indian-flag)
"""

import argparse
import shutil
import sys
import os
import math
import platform
import subprocess
import urllib.request
import re
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# === Constants ===
WIDTH, HEIGHT = 1080, 1080
CHAKRA_RADIUS, CHAKRA_SPOKES = 100, 24
FOOTER_HEIGHT = 100
HEADER_HEIGHT = 100
FONT_URL = "https://github.com/google/fonts/raw/refs/heads/main/ofl/hindmadurai/HindMadurai-Bold.ttf"
FONT_NAME = "HindMadurai-Bold.ttf"

# === Validation ===
def validate_name(name: str) -> str:
    """Validate footer name for allowed characters and length."""
    name = name.strip()
    if not (2 <= len(name) <= 30):
        raise argparse.ArgumentTypeError("❌ Name must be between 2 and 30 characters.")
    if not re.match(r"^[A-Za-z0-9\s.,'-]+$", name):
        raise argparse.ArgumentTypeError("❌ Name contains invalid characters.")
    return name

# === Font Handling ===
def get_font_path() -> str:
    """Download HindMadurai-Bold.ttf font into current script directory if missing."""
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FONT_NAME)

    if not os.path.exists(font_path):
        print("📥 Downloading HindMadurai Bold font...")
        try:
            urllib.request.urlretrieve(FONT_URL, font_path)
            print("✅ Font downloaded.")
        except Exception as e:
            print(f"⚠ Could not download font: {e}. Using default font.")
            return ""
    return font_path

def paste_emoji(img, x, y, size=40, emoji_code="1f54a"):
    """Paste emoji as PNG to avoid missing glyph issues."""
    try:
        emoji_url = f"https://github.com/twitter/twemoji/raw/master/assets/72x72/{emoji_code}.png"
        r = requests.get(emoji_url, timeout=5)
        emoji_img = Image.open(BytesIO(r.content)).convert("RGBA")
        emoji_img = emoji_img.resize((size, size), Image.LANCZOS)
        img.paste(emoji_img, (x, y), emoji_img)
    except Exception as e:
        print(f"⚠ Could not load emoji image: {e}")

# === Drawing ===
def draw_ashoka_chakra(draw: ImageDraw.Draw, cx: int, cy: int):
    """Draw Ashoka Chakra in center."""
    draw.ellipse(
        (cx - CHAKRA_RADIUS, cy - CHAKRA_RADIUS, cx + CHAKRA_RADIUS, cy + CHAKRA_RADIUS),
        outline="#000080", width=6
    )
    for i in range(CHAKRA_SPOKES):
        angle = math.radians(i * (360 / CHAKRA_SPOKES))
        ex = cx + CHAKRA_RADIUS * math.cos(angle)
        ey = cy + CHAKRA_RADIUS * math.sin(angle)
        draw.line((cx, cy, ex, ey), fill="#000080", width=3)

def draw_small_chakra(draw: ImageDraw.Draw, cx: int, cy: int, radius: int = 20, spokes: int = 24):
    """Draw a small Ashoka Chakra (scaled) for footer/header."""
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        outline="#000080", width=2
    )
    for i in range(spokes):
        angle = math.radians(i * (360 / spokes))
        ex = cx + radius * math.cos(angle)
        ey = cy + radius * math.sin(angle)
        draw.line((cx, cy, ex, ey), fill="#000080", width=1)

def draw_vertical_gradient(draw, box, top_color, bottom_color):
    """Draw vertical gradient."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    for i in range(h):
        ratio = i / h
        r = round(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = round(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = round(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))

def draw_gradient_text(img, position, text, font, start_color, end_color):
    """Draw gradient text with mask blending."""
    mask = Image.new("L", img.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text(position, text, font=font, fill=255)

    gradient = Image.new("RGB", img.size)
    grad_draw = ImageDraw.Draw(gradient)

    try:
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        try:
            tw, th = ImageDraw.Draw(Image.new("RGB", (1, 1))).textsize(text, font=font)
        except AttributeError:
            tw, th = font.getsize(text)

    for y in range(th):
        ratio = y / th
        r = round(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = round(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = round(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        grad_draw.line(
            [(position[0], position[1] + y), (position[0] + tw, position[1] + y)],
            fill=(r, g, b)
        )

    img.paste(gradient, mask=mask)

# === Main Flag Creation ===
def create_flag_with_footer(name: str, output_path: str):
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    flag_height = HEIGHT - FOOTER_HEIGHT
    stripe_h = (flag_height - HEADER_HEIGHT) // 3

    # Stripes
    draw.rectangle([0, HEADER_HEIGHT, WIDTH, HEADER_HEIGHT + stripe_h], fill="#FF9933")
    draw.rectangle([0, HEADER_HEIGHT + stripe_h, WIDTH, HEADER_HEIGHT + stripe_h * 2], fill="white")
    draw.rectangle([0, HEADER_HEIGHT + stripe_h * 2, WIDTH, HEIGHT - FOOTER_HEIGHT], fill="#138808")

    # Chakra center
    draw_ashoka_chakra(draw, WIDTH // 2, HEADER_HEIGHT + stripe_h + stripe_h // 2)

    # Header gradient
    draw_vertical_gradient(draw, (0, 0, WIDTH, HEADER_HEIGHT // 2), (255, 153, 51), (255, 255, 255))
    draw_vertical_gradient(draw, (0, HEADER_HEIGHT // 2, WIDTH, HEADER_HEIGHT),
                           (255, 255, 255), (19, 136, 8))

    # Footer gradient
    draw_vertical_gradient(draw, (0, HEIGHT - FOOTER_HEIGHT, WIDTH, HEIGHT - FOOTER_HEIGHT // 2),
                           (255, 153, 51), (255, 255, 255))
    draw_vertical_gradient(draw, (0, HEIGHT - FOOTER_HEIGHT // 2, WIDTH, HEIGHT),
                           (255, 255, 255), (19, 136, 8))

    font_path = get_font_path()
    font = ImageFont.truetype(font_path, 40) if font_path else ImageFont.load_default()

    # === HEADER text + chakra + emoji ===
    header_text = "Happy Independence Day"
    try:
        bbox = draw.textbbox((0, 0), header_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        tw, th = draw.textsize(header_text, font=font)

    chakra_radius = 23
    spacing = 12
    total_width = chakra_radius * 2 + spacing + tw
    tx = (WIDTH - total_width) // 2 + chakra_radius * 2 + spacing
    ty = (HEADER_HEIGHT - th) // 2

    # chakra_cx = tx - spacing - chakra_radius
    # chakra_cy = ty + th // 2
    # draw_small_chakra(draw, chakra_cx, chakra_cy, radius=chakra_radius)
    draw_gradient_text(img, (tx, ty), header_text, font, (255, 153, 51), (19, 136, 8))
    paste_emoji(img, tx + tw + 10, ty - 5, size=th + 5, emoji_code="1f54a")

    # === FOOTER text + chakra + emoji ===
    try:
        bbox = draw.textbbox((0, 0), name, font=font)
        ftw = bbox[2] - bbox[0]
        fth = bbox[3] - bbox[1]
    except AttributeError:
        ftw, fth = draw.textsize(name, font=font)

    total_width_footer = ftw + spacing + (fth + 5)
    ftx = (WIDTH - total_width_footer) // 2
    fty = HEIGHT - FOOTER_HEIGHT + (FOOTER_HEIGHT - fth) // 2

    # chakra_cx_footer = ftx - spacing - chakra_radius
    # chakra_cy_footer = fty + fth // 2
    # draw_small_chakra(draw, chakra_cx_footer, chakra_cy_footer, radius=chakra_radius)
    draw_gradient_text(img, (ftx, fty), name, font, (255, 153, 51), (19, 136, 8))
    paste_emoji(img, ftx + ftw + 10, fty - 5, size=fth + 5, emoji_code="1f54a")

    img.save(output_path, "PNG")
    return output_path

# === Image Opening ===
def open_image(path: str):
    try:
        sys_platform = platform.system()
        if sys_platform == "Darwin":
            subprocess.run(["open", path], check=False)
        elif sys_platform == "Windows":
            os.startfile(path)  # type: ignore
        elif sys_platform == "Linux":
            if "com.termux" in os.getenv("PREFIX", ""):
                if shutil.which("termux-open"):
                    subprocess.run(["termux-open", path], check=False)
                else:
                    print(f"⚠ termux-open not found. Image saved at: {path}")
            else:
                if shutil.which("xdg-open"):
                    subprocess.run(["xdg-open", path], check=False)
                else:
                    print(f"⚠ xdg-open not found. Image saved at: {path}")
        else:
            print(f"⚠ Unsupported platform. Image saved at: {path}")
    except Exception as e:
        print(f"⚠ Could not open image: {e}")

# === CLI Entrypoint ===
def main():
    parser = argparse.ArgumentParser(
        description="Create Indian Flag with your Name",
        usage="%(prog)s 'Your Name' [-o output.png]"
    )
    parser.add_argument("name", type=validate_name, help="Footer name (2-30 chars)")
    parser.add_argument("-o", "--output", default="indian_flag.png", help="Output image file")
    args = parser.parse_args()

    # === Detect OS and adjust output folder ===
    sys_platform = platform.system()
    if sys_platform == "Linux" and "com.termux" in os.getenv("PREFIX", ""):
        termux_paths = [
            os.path.expanduser("~/storage/downloads"),
            os.path.expanduser("~/storage/Download")
        ]
        downloads_dir = next((p for p in termux_paths if os.path.isdir(p)), termux_paths[0])
    elif sys_platform == "Linux":
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    elif sys_platform == "Windows":
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    elif sys_platform == "Darwin":
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    else:
        downloads_dir = os.path.expanduser("~")  # fallback

    # Ensure the folder exists
    os.makedirs(downloads_dir, exist_ok=True)

    # Build full path
    output_path = os.path.join(downloads_dir, args.output)

    try:
        path = create_flag_with_footer(args.name, output_path)
        print(f"✅ Flag image saved to {path}")
        open_image(path)
    except KeyboardInterrupt:
        print("\n⚠ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
