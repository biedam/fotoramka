# TODO:
# After image upload:
# - read image orientation
# - read exif data
# - crop image to 2:3 aspect ratio
# - scale image to 1600 x 1200 size
# - save the image on disc
# Before displaying:
# - display the image -> perform dithering and annotations

import subprocess
from pathlib import Path

class Photo:
    def __init__(self, image_path):
        self.image_path = image_path
        utils_dir = Path(__file__).parent
        self.dither_palette = utils_dir / "palette.bmp"
        self.processing_path = "img.png"

    def dither(self, diffusion):
        diffusion_amount = f"dither:diffusion-amount={diffusion}%"
        dither_command = ['convert', self.image_path, '-dither', 'FloydSteinberg', '-define', diffusion_amount, '-remap', self.dither_palette, '-type', 'truecolor', self.processing_path]
        subprocess.run(dither_command, check=True)

    def annotate(self, position, font_size, text):
        file_in = self.processing_path
        file_out = self.processing_path
        font = "Virgil3YOFF"
        partial_cmd = ['-gravity', position, '-font', font, '-pointsize', f'{font_size}', '-annotate', '0', f"\'{text}\'"]
        annotation_command = ['convert', file_in, '-strokewidth', '3', '-stroke', 'black'] + partial_cmd + ['-fill', 'white', '-strokewidth', '1', '-stroke', 'white'] + partial_cmd + [file_out]
        subprocess.run(annotation_command, check=True)