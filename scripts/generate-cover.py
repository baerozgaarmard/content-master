import os
import sys
import math
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

def add_sticker_contour(img, outline_width=8, outline_color=(255, 255, 255, 255), shadow_offset=(0, 10), shadow_blur=12, shadow_color=(0, 0, 0, 180)):
    w, h = img.size
    pad = outline_width * 2 + shadow_blur * 2 + abs(shadow_offset[0]) + abs(shadow_offset[1])
    canvas_w = w + pad * 2
    canvas_h = h + pad * 2
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    
    # Create mask canvas
    base_mask = Image.new("L", (canvas_w, canvas_h), 0)
    base_mask.paste(img.split()[-1], (pad, pad))
    
    # 1. Shadow
    shadow_mask = base_mask.filter(ImageFilter.MaxFilter(outline_width * 2 + 1)).filter(ImageFilter.GaussianBlur(shadow_blur))
    shadow_offset_mask = Image.new("L", (canvas_w, canvas_h), 0)
    shadow_offset_mask.paste(shadow_mask, shadow_offset)
    shadow_layer = Image.new("RGBA", (canvas_w, canvas_h), shadow_color)
    canvas.paste(shadow_layer, (0, 0), mask=shadow_offset_mask)
    
    # 2. Outline
    outline_mask = base_mask.filter(ImageFilter.MaxFilter(outline_width * 2 + 1))
    outline_layer = Image.new("RGBA", (canvas_w, canvas_h), outline_color)
    canvas.paste(outline_layer, (0, 0), mask=outline_mask)
    
    # 3. Base image
    canvas.paste(img, (pad, pad), mask=img.split()[-1])
    return canvas

def draw_text_with_stroke(draw, xy, text, font, fill_color, stroke_color, stroke_width=8, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 220)):
    x, y = xy
    # Shadow
    if shadow_color:
        sx, sy = shadow_offset
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                draw.text((x + sx + dx, y + sy + dy), text, font=font, fill=shadow_color)
    # Stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx*dx + dy*dy <= stroke_width*stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    # Fill
    draw.text((x, y), text, font=font, fill=fill_color)

def main():
    parser = argparse.ArgumentParser(description="Ayush Pipeline - Viral 1080x1920 Cover Generator")
    parser.add_argument("--topic", default="prompts-chat", help="Topic slug")
    parser.add_argument("--title1", default="STOP PAYING FOR", help="Headline Line 1")
    parser.add_argument("--title2", default="CHATGPT PROMPTS!", help="Headline Line 2")
    parser.add_argument("--badge", default="★ 174,000 STARS ON GITHUB  |  100% FREE", help="Top badge text")
    parser.add_argument("--pill", default="SECRET CHEAT CODE 🤫 100% FREE", help="Pill hook text")
    parser.add_argument("--cta", default="github.com/f/prompts.chat", help="Bottom CTA text")
    parser.add_argument("--screenshot", default=None, help="Path to repo screenshot overlay")
    parser.add_argument("--output", default=None, help="Output image file path")
    args = parser.parse_args()

    root = r"C:\Users\Ayush\.gemini\antigravity\scratch\content-master"
    bg_path = os.path.join(root, "assets", "thumbnails", "bg_28.jpg")
    peter_path = os.path.join(root, "packages", "faceless", "skills", "faceless", "Characters", "Peter.png")
    stewie_path = os.path.join(root, "packages", "faceless", "skills", "faceless", "Characters", "Stewie.png")
    repo_card_path = args.screenshot or os.path.join(root, "assets", "overlays", "real_github_repo_overview.png")
    
    # 1. Base Canvas 1080x1920
    bg = Image.open(bg_path).convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
    
    # Color grade background: boost saturation & contrast, add slight blur for depth
    bg = ImageEnhance.Color(bg).enhance(1.25)
    bg = ImageEnhance.Contrast(bg).enhance(1.15)
    
    # Add dark vignette gradient overlay
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)
    
    # Dark radial center-to-edge
    for y in range(1920):
        # Darkness factor: highest at top & bottom
        if y < 700:
            alpha = int(140 * (1.0 - (y / 700.0) * 0.5))
        elif y > 1100:
            alpha = int(180 * ((y - 1100.0) / 820.0))
        else:
            alpha = 70
        d_overlay.line([(0, y), (1080, y)], fill=(10, 15, 30, alpha))
        
    bg = Image.alpha_composite(bg, overlay)
    
    # 2. Add Project / Repo Screenshot Card (Center Top)
    if os.path.exists(repo_card_path):
        repo_img = Image.open(repo_card_path).convert("RGBA")
        # Resize to fit width 960 while maintaining aspect ratio
        card_w = 940
        card_h = int(repo_img.height * (card_w / repo_img.width))
        if card_h > 520:
            card_h = 520
            card_w = int(repo_img.width * (card_h / repo_img.height))
        repo_resized = repo_img.resize((card_w, card_h), Image.Resampling.LANCZOS)
        
        # Rounded corners & border
        corner_radius = 24
        mask_corner = Image.new("L", (card_w, card_h), 0)
        draw_corner = ImageDraw.Draw(mask_corner)
        draw_corner.rounded_rectangle((0, 0, card_w, card_h), radius=corner_radius, fill=255)
        
        # Sticker outline + shadow for the screenshot card
        card_sticker = add_sticker_contour(
            repo_resized, 
            outline_width=6, 
            outline_color=(56, 189, 248, 255),  # Electric cyan border
            shadow_offset=(0, 16), 
            shadow_blur=24, 
            shadow_color=(0, 0, 0, 220)
        )
        # Center card at y=230
        card_x = (1080 - card_sticker.width) // 2
        bg.paste(card_sticker, (card_x, 210), mask=card_sticker)
    
    # 3. Add Viral Top Badge
    draw = ImageDraw.Draw(bg)
    font_bold = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", 34)
    font_title = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", 78)
    font_sub = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", 84)
    font_pill = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", 36)
    
    badge_text = args.badge
    b_bbox = draw.textbbox((0, 0), badge_text, font=font_bold)
    bw, bh = b_bbox[2] - b_bbox[0], b_bbox[3] - b_bbox[1]
    bx = (1080 - (bw + 60)) // 2
    by = 110
    
    # Badge backdrop (dark pill with gold border)
    draw.rounded_rectangle((bx - 3, by - 3, bx + bw + 63, by + bh + 31), radius=22, fill=(255, 215, 0, 255))
    draw.rounded_rectangle((bx, by, bx + bw + 60, by + bh + 28), radius=20, fill=(15, 23, 42, 250))
    draw.text((bx + 30, by + 12), badge_text, font=font_bold, fill=(255, 215, 0, 255))
    
    # 4. Viral Main Headline (y=800 to 1120)
    # Line 1:
    l1_text = args.title1
    l1_bbox = draw.textbbox((0, 0), l1_text, font=font_title)
    l1_x = (1080 - (l1_bbox[2] - l1_bbox[0])) // 2
    draw_text_with_stroke(draw, (l1_x, 800), l1_text, font_title, (255, 255, 255), (0, 0, 0), stroke_width=12)
    
    # Line 2:
    l2_text = args.title2
    l2_bbox = draw.textbbox((0, 0), l2_text, font=font_sub)
    l2_x = (1080 - (l2_bbox[2] - l2_bbox[0])) // 2
    # Gold fill with black stroke
    draw_text_with_stroke(draw, (l2_x, 900), l2_text, font=font_sub, fill_color=(255, 230, 0), stroke_color=(0, 0, 0), stroke_width=14, shadow_color=(255, 60, 0, 180))
    
    # Line 3: Pill Hook:
    pill_text = args.pill
    p_bbox = draw.textbbox((0, 0), pill_text, font=font_pill)
    pw, ph = p_bbox[2] - p_bbox[0], p_bbox[3] - p_bbox[1]
    px = (1080 - (pw + 70)) // 2
    py = 1045
    # Neon green glow pill
    draw.rounded_rectangle((px - 4, py - 4, px + pw + 74, py + ph + 34), radius=28, fill=(0, 255, 128, 255))
    draw.rounded_rectangle((px, py, px + pw + 70, py + ph + 30), radius=25, fill=(10, 10, 10, 245))
    draw.text((px + 35, py + 14), pill_text, font=font_pill, fill=(0, 255, 128, 255))
    
    # 5. Characters at Bottom: Peter (Left) & Stewie (Right)
    peter = Image.open(peter_path).convert("RGBA")
    stewie = Image.open(stewie_path).convert("RGBA")
    
    # Scale characters
    peter_scaled = peter.resize((480, 800), Image.Resampling.LANCZOS)
    stewie_scaled = stewie.resize((432, 720), Image.Resampling.LANCZOS)
    
    # Add sticker contours
    peter_sticker = add_sticker_contour(peter_scaled, outline_width=9, outline_color=(255, 255, 255, 255), shadow_offset=(-5, 12), shadow_blur=16)
    stewie_sticker = add_sticker_contour(stewie_scaled, outline_width=9, outline_color=(255, 255, 255, 255), shadow_offset=(5, 12), shadow_blur=16)
    
    # Paste Peter at left-bottom
    bg.paste(peter_sticker, (-30, 1140), mask=peter_sticker)
    
    # Paste Stewie at right-bottom
    bg.paste(stewie_sticker, (640, 1220), mask=stewie_sticker)
    
    # Center CTA Pill between characters
    cta_text = args.cta
    font_cta = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", 32)
    c_bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    cw, ch = c_bbox[2] - c_bbox[0], c_bbox[3] - c_bbox[1]
    cx = (1080 - (cw + 50)) // 2
    cy = 1780
    draw.rounded_rectangle((cx, cy, cx + cw + 50, cy + ch + 26), radius=20, fill=(30, 41, 59, 230), outline=(56, 189, 248), width=3)
    draw.text((cx + 25, cy + 12), cta_text, font=font_cta, fill=(255, 255, 255))
    
    # Save outputs
    if args.output:
        out_cover = args.output
        os.makedirs(os.path.dirname(os.path.abspath(out_cover)), exist_ok=True)
    else:
        out_dir = os.path.join(root, "faceless-output", "thumbnails", args.topic)
        os.makedirs(out_dir, exist_ok=True)
        out_cover = os.path.join(out_dir, "cover.png")

    bg.save(out_cover, quality=95)
    print("Cover generated:", out_cover, "Size:", os.path.getsize(out_cover))

if __name__ == "__main__":
    main()
