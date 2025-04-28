import argparse
import sys
import os
from epd_drv import epd13in3E
from PIL import Image
import time

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


def main():
    parser = argparse.ArgumentParser(description="Command line interface for Fotoramka APP - for test&debug", add_help=True)

    parser.add_argument('-clear', action='store_true', help='Clear EPD screen')
    parser.add_argument('-display', type=str, metavar='plik', help='Display image on EPD')

    args = parser.parse_args()

    if args.clear:
        epd_clear()
    elif args.display:
        disp_img(args.display)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

