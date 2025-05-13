import argparse
import sys
import os
#from epd_drv import epd13in3E
from PIL import Image
import time
from utils.photo import Photo
from utils.frame import Frame
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s', level=logging.INFO)

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')

#epd = epd13in3E.EPD()

def epd_clear():
    img = Photo("")
    img.clear()

def disp_img(path):
    print(f"Display image: {path}")
    start_time = time.time()
    img = Photo(path)
    img.set_palette(img.PALETTE2)
    img.display(path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"🕒 Execution time: {elapsed_time:.2f} s")

def img_dither(dither_amout, file_path):
    start_time = time.time()
    img = Photo(file_path)
    img.set_palette(img.PALETTE2)
    img.dither(dither_amout)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"🕒 Execution time: {elapsed_time:.2f} s")

def img_annotate(text, file_path):
    start_time = time.time()
    img = Photo(file_path)
    img.annotate('South',40,text)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"🕒 Execution time: {elapsed_time:.2f} s")

def img_resize(file_path):
    start_time = time.time()
    img = Photo(file_path)
    orient = img.resize("resized.jpg")
    #orient = img.resize(file_path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"🕒 Execution time: {elapsed_time:.2f} s")
    print(orient)

def img_get_exif(file_path):
    img = Photo(file_path)
    exif_data = img.get_exif()
    print(exif_data)

def orientation():
    frm = Frame()
    frm.orientation()

def rotate(direction):
    frm = Frame()
    frm.rotate(direction)

def main():
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description="Command line interface for Fotoramka APP - for test&debug", add_help=True)

    parser.add_argument('-clear', action='store_true', help='Clear EPD screen')
    parser.add_argument('-display', action='store_true', help='Display image on EPD')
    parser.add_argument('-dither', type=int, help='Dithering level (eg. 80)')
    parser.add_argument('-annotate', type=str, help='Annotate image with text')
    parser.add_argument('-f', type=str, help='Path to image file')
    parser.add_argument('-resize', action='store_true', help='Resize and crop the image')
    parser.add_argument('-exif', action='store_true', help='Get image EXIF data')
    parser.add_argument('-angle', action='store_true', help='Get frame orientation')
    parser.add_argument('-rotate', type=float, help='Rotate frame')

    args = parser.parse_args()

    if args.clear:
        epd_clear()
    elif args.display:
        disp_img(args.f)
    elif args.dither:
        img_dither(args.dither, args.f)
    elif args.annotate:
        img_annotate(args.annotate, args.f)
    elif args.resize:
        img_resize(args.f)
    elif args.exif:
        img_get_exif(args.f)
    elif args.angle:
        orientation()
    elif args.rotate:
        rotate(args.rotate)
    else:
        parser.print_help()

    logging.info('Watch out!')

if __name__ == "__main__":
    main()

