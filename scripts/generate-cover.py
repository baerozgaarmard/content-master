import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

def add_clean_contour(img, outline_width=6, outline_color=(255, 255, 255, 255), shadow_offset=(0, 10), shadow_blur=12, shadow_color=(0, 0, 0, 190)):
    w, h = img.size
    pad = outline_width * 2 + shadow_blur * 2 + abs(shadow_offset[0]) + abs(shadow_offset[1])
    canvas_w = w + pad * 2
    canvas_h = h + pad * 2
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    
    base_mask = Image.new("L", (canvas_w, canvas_h), 0)
    base_mask.paste(img.split()[-1], (pad, pad))
    
    # Shadow
    shadow_mask = base_mask.filter(ImageFilter.MaxFilter(outline_width * 2 + 1)).filter(ImageFilter.GaussianBlur(shadow_blur))
    shadow_offset_mask = Image.new("L", (canvas_w, canvas_h), 0)
    shadow_offset_mask.paste(shadow_mask, shadow_offset)
    shadow_layer = Image.new("RGBA", (canvas_w, canvas_h), shadow_color)
    canvas.paste(shadow_layer, (0, 0), mask=shadow_offset_mask)
    
    # Clean outline
    outline_mask = base_mask.filter(ImageFilter.MaxFilter(outline_width * 2 + 1))
    outline_layer = Image.new("RGBA", (canvas_w, canvas_h), outline_color)
    canvas.paste(outline_layer, (0, 0), mask=outline_mask)
    
    # Base image
    canvas.paste(img, (pad, pad), mask=img.split()[-1])
    return canvas

def draw_bold_stroke_text(draw, xy, text, font, fill_color, stroke_color, stroke_width=10, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 220)):
    x, y = xy
    if shadow_color:
        sx, sy = shadow_offset
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                draw.text((x + sx + dx, y + sy + dy), text, font=font, fill=shadow_color)
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx*dx + dy*dy <= stroke_width*stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    draw.text((x, y), text, font=font, fill=fill_color)

def main():
    parser = argparse.ArgumentParser(description="Ayush Pipeline - Clean Real-Repo Viral Thumbnail Generator")
    parser.add_argument("--topic", default="ponytail", help="Topic slug")
    parser.add_argument("--title1", default="STOP LETTING AI", help="Headline Line 1")
    parser.add_argument("--title2", default="WRITE BLOATED CODE!", help="Headline Line 2")
    parser.add_argument("--screenshot", default=None, help="Path to real repo screenshot")
    parser.add_argument("--output", default=None, help="Output cover image path")
    args = parser.parse_args()

    root = r"C:\Users\Ayush\.gemini\antigravity\scratch\content-master"
    bg_path = os.path.join(root, "assets", "thumbnails", "bg_28.jpg")
    peter_path = os.path.join(root, "skills", "faceless", "Characters", "Peter.png")
    stewie_path = os.path.join(root, "skills", "faceless", "Characters", "Stewie.png")
    
    # Real repo screenshot
    repo_shot_path = args.screenshot or os.path.join(root, "assets", "overlays", "ponytail_real", "real_repo_main.png")
    
    # 1. Base Canvas 1080x1920
    bg = Image.open(bg_path).convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
    bg = ImageEnhance.Color(bg).enhance(1.2)
    bg = ImageEnhance.Contrast(bg).enhance(1.15)
    
    # Dark vignette gradient (focus viewer attention on headline and real screenshot)
    vignette = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d_vig = ImageDraw.Draw(vignette)
    for y in range(1920):
        if y < 450:
            alpha = int(180 * (1.0 - (y / 450.0) * 0.3))
        elif y > 1250:
            alpha = int(210 * ((y - 1250.0) / 670.0))
        else:
            alpha = 110
        d_vig.line([(0, y), (1080, y)], fill=(10, 14, 24, alpha))
    bg = Image.alpha_composite(bg, vignette)
    
    draw = ImageDraw.Draw(bg)
    font_headline = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", 82)
    font_sub = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", 80)
    
    # 2. Clean, Bold Viral Headline (NO AI SLOP BOXES, NO SYNTHETIC PILLS)
    # Line 1
    l1_bbox = draw.textbbox((0, 0), args.title1, font=font_headline)
    l1_x = (1080 - (l1_bbox[2] - l1_bbox[0])) // 2
    draw_bold_stroke_text(draw, (l1_x, 140), args.title1, font_headline, (255, 255, 255), (0, 0, 0), stroke_width=12)
    
    # Line 2 (Vibrant yellow accent)
    l2_bbox = draw.textbbox((0, 0), args.title2, font=font_sub)
    l2_x = (1080 - (l2_bbox[2] - l2_bbox[0])) // 2
    draw_bold_stroke_text(draw, (l2_x, 245), args.title2, font_sub, (255, 230, 0), (0, 0, 0), stroke_width=14, shadow_color=(200, 30, 0, 180))
    
    # 3. REAL GITHUB REPOSITORY SCREENSHOT (Centerpiece)
    if os.path.exists(repo_shot_path):
        repo_img = Image.open(repo_shot_path).convert("RGBA")
        # Target width 1000px, aspect-ratio preserved
        card_w = 980
        aspect = repo_img.height / repo_img.width
        card_h = int(card_w * aspect)
        if card_h > 720:
            card_h = 720
            card_w = int(card_h / aspect)
            
        repo_resized = repo_img.resize((card_w, card_h), Image.Resampling.LANCZOS)
        
        # Frame with clean rounded border and drop shadow (mimicking a crisp desktop browser window)
        radius = 18
        mask_corner = Image.new("L", (card_w, card_h), 0)
        draw_c = ImageDraw.Draw(mask_corner)
        draw_c.rounded_rectangle((0, 0, card_w, card_h), radius=radius, fill=255)
        
        # Shadow
        pad = 24
        canvas_card = Image.new("RGBA", (card_w + pad*2, card_h + pad*2), (0, 0, 0, 0))
        shadow_mask = mask_corner.filter(ImageFilter.GaussianBlur(16))
        shadow_layer = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 220))
        canvas_card.paste(shadow_layer, (pad, pad + 10), mask=shadow_mask)
        
        # Base image
        card_base = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        card_base.paste(repo_resized, (0, 0), mask=mask_corner)
        
        # Clean subtle border (GitHub dark cyan/slate border)
        draw_cb = ImageDraw.Draw(card_base)
        draw_cb.rounded_rectangle((1, 1, card_w - 2, card_h - 2), radius=radius, outline=(56, 189, 248, 255), width=3)
        
        canvas_card.paste(card_base, (pad, pad), mask=card_base)
        
        card_x = (1080 - canvas_card.width) // 2
        card_y = 390
        bg.paste(canvas_card, (card_x, card_y), mask=canvas_card)
        
    # 4. Character Cutouts (Peter on Left, Stewie on Right)
    peter = Image.open(peter_path).convert("RGBA")
    stewie = Image.open(stewie_path).convert("RGBA")
    
    peter_scaled = peter.resize((480, 800), Image.Resampling.LANCZOS)
    stewie_scaled = stewie.resize((432, 720), Image.Resampling.LANCZOS)
    
    peter_cont = add_clean_contour(peter_scaled, outline_width=8, outline_color=(255, 255, 255, 255), shadow_offset=(-4, 10), shadow_blur=14)
    stewie_cont = add_clean_contour(stewie_scaled, outline_width=8, outline_color=(255, 255, 255, 255), shadow_offset=(4, 10), shadow_blur=14)
    
    bg.paste(peter_cont, (-30, 1150), mask=peter_cont)
    bg.paste(stewie_cont, (650, 1220), mask=stewie_cont)
    
    # Save output
    out_file = args.output or os.path.join(root, "faceless-output", "thumbnails", args.topic, "cover.png")
    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    bg.save(out_file, quality=95)
    print(f"Clean real-repo cover generated -> {out_file} ({os.path.getsize(out_file)} bytes)")

if __name__ == "__main__":
    main()
