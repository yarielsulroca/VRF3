#!/usr/bin/env python3
"""
Genera un icono.ico simple para la app.
Ejecutar: python assets/generate_icon.py
Requiere: pip install pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    images = []

    for size in sizes:
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fondo azul redondeado
        margin = size[0] // 8
        draw.rounded_rectangle(
            [margin, margin, size[0]-margin, size[1]-margin],
            radius=size[0]//5,
            fill=(30, 100, 200, 255)
        )

        # Texto "VC" o símbolo $
        try:
            font_size = size[0] // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = "$"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size[0] - text_w) // 2
        y = (size[1] - text_h) // 2 - size[1]//16
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

        images.append(img)

    output_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    print(f"✅ Icono generado: {output_path}")

if __name__ == "__main__":
    create_icon()