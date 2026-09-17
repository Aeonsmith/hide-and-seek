import os
from PIL import Image, ImageDraw

def generate_icon(output_path="icon.ico"):
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for width, height in sizes:
        # Create image with transparent background
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw rounded background badge
        margin = max(1, width // 16)
        radius = width // 5
        draw.rounded_rectangle(
            [margin, margin, width - margin, height - margin],
            radius=radius,
            fill=(26, 29, 36, 255),
            outline=(59, 130, 246, 255),
            width=max(1, width // 32),
        )

        # Draw film strip / play triangle / scissors symbol
        center_x, center_y = width // 2, height // 2
        size = width // 3

        # Film reels / accents
        accent_color = (96, 165, 250, 255)
        neon_accent = (244, 63, 94, 255)

        # Video symbol (play triangle)
        pt1 = (center_x - size // 2, center_y - size // 2)
        pt2 = (center_x - size // 2, center_y + size // 2)
        pt3 = (center_x + size // 2, center_y)
        draw.polygon([pt1, pt2, pt3], fill=accent_color)

        # Audio waveform dots/bars on top right
        bar_w = max(1, width // 24)
        bar_gap = max(1, width // 32)
        start_x = width - margin - (bar_w + bar_gap) * 3 - margin // 2
        for i, h_factor in enumerate([0.2, 0.4, 0.3]):
            bar_h = int(height * h_factor)
            bx = start_x + i * (bar_w + bar_gap)
            by = height // 2 - bar_h // 2
            draw.rectangle([bx, by, bx + bar_w, by + bar_h], fill=neon_accent)

        images.append(img)

    images[0].save(
        output_path,
        format="ICO",
        sizes=[(s[0], s[1]) for s in sizes],
        append_images=images[1:],
    )
    print(f"Icon generated successfully: {output_path}")

if __name__ == "__main__":
    generate_icon()
