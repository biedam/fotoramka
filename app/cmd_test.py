import argparse
import sys
import os
from epd_drv import epd13in3E
from PIL import Image
import time
from utils.photo import Photo

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')

epd = epd13in3E.EPD()

def epd_clear():
    try:
        epd.Init()
        print("clearing...")
        epd.Clear()
        time.sleep(3)
        print("goto sleep...")
        epd.sleep()
        print("EPD cleared")
    except:
        print("goto sleep...")
        epd.sleep()

def disp_img(path):
    print(f"Display image: {path}")
    try:
        epd.Init()
        print("clearing...")

        # Drawing on the image
        print("1.Drawing on the image...")
        Himage = Image.new('RGB', (epd.width, epd.height), epd.WHITE)  # 255: clear the frame

        # read bmp file 
        print("2.read bmp file")
        Himage = Image.open(os.path.join(picdir, 'test2.jpg'))
        epd.display(epd.getbuffer(Himage))
        time.sleep(3)


        print("goto sleep...")
        epd.sleep()
    except:
        print("goto sleep...")
        epd.sleep()

def img_dither(dither_amout, file_path):
    img = Photo(file_path)
    img.dither(dither_amout)

def img_annotate(text, file_path):
    img = Photo(file_path)
    img.annotate('South',80,text)

def main():
    parser = argparse.ArgumentParser(description="Command line interface for Fotoramka APP - for test&debug", add_help=True)

    parser.add_argument('-clear', action='store_true', help='Clear EPD screen')
    parser.add_argument('-display', action='store_true', help='Display image on EPD')
    parser.add_argument('-dither', type=int, help='Dithering level (eg. 80)')
    parser.add_argument('-annotate', type=str, help='Annotate image with text')
    parser.add_argument('-f', type=str, help='Path to image file')

    args = parser.parse_args()

    if args.clear:
        epd_clear()
    elif args.display:
        disp_img(args.f)
    elif args.dither:
        img_dither(args.dither, args.f)
    elif args.annotate:
        img_annotate(args.annotate, args.f)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

