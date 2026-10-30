import math
from PIL import Image, ImageDraw

def draw_soccer_ball(size: int, output_path: str):
    # Create image with transparent background (or dark circle background for maskable)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size / 2.0
    radius = size * 0.44

    # Background circle (ball body)
    # Give a subtle 3D lighting gradient by drawing layered circles
    for r in range(int(radius), 0, -1):
        ratio = r / radius
        # Slight gradient from top-left
        col = int(225 + 30 * (1 - ratio))
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(col, col, col, 255)
        )

    # Dark outer border
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        outline=(20, 30, 45, 255),
        width=max(2, int(size * 0.025))
    )

    # Pentagon in center
    p_radius = radius * 0.38
    pentagon_points = []
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        px = center + p_radius * math.cos(angle)
        py = center + p_radius * math.sin(angle)
        pentagon_points.append((px, py))
    draw.polygon(pentagon_points, fill=(15, 23, 42, 255), outline=(30, 41, 59, 255))

    # Outer radiating patches
    line_w = max(2, int(size * 0.02))
    outer_patches = []
    for i in range(5):
        # Ray from pentagon vertex outwards
        v1 = pentagon_points[i]
        angle = math.radians(i * 72 - 90)
        v2_x = center + radius * 0.75 * math.cos(angle)
        v2_y = center + radius * 0.75 * math.sin(angle)
        draw.line([v1, (v2_x, v2_y)], fill=(30, 41, 59, 255), width=line_w)

        # Polygon at the edge
        angle_l = angle - math.radians(24)
        angle_r = angle + math.radians(24)
        ex1 = center + radius * math.cos(angle_l)
        ey1 = center + radius * math.sin(angle_l)
        ex2 = center + radius * math.cos(angle_r)
        ey2 = center + radius * math.sin(angle_r)
        
        patch = [(v2_x, v2_y), (ex2, ey2), (ex1, ey1)]
        draw.polygon(patch, fill=(15, 23, 42, 255), outline=(30, 41, 59, 255))
        outer_patches.append((v2_x, v2_y))

    # Connecting lines between outer patches
    for i in range(5):
        p1 = outer_patches[i]
        p2 = outer_patches[(i + 1) % 5]
        draw.line([p1, p2], fill=(30, 41, 59, 255), width=line_w)

    img.save(output_path, "PNG")
    print(f"Generated: {output_path} ({size}x{size})")

if __name__ == "__main__":
    draw_soccer_ball(192, r"c:\Users\user\Downloads\betmins\static\icon-192.png")
    draw_soccer_ball(512, r"c:\Users\user\Downloads\betmins\static\icon-512.png")
    draw_soccer_ball(64, r"c:\Users\user\Downloads\betmins\static\favicon.png")
