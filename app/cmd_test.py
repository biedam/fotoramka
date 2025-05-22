import argparse
import sys
import os
#from epd_drv import epd13in3E
from PIL import Image
import time
from utils.photo import Photo, Orientation
from utils.frame import Frame
from utils.photoalbum import PhotoAlbum, initdb
from pathlib import Path
from uuid import uuid4
import shutil
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s', level=logging.INFO)

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')

#epd = epd13in3E.EPD()
UPLOAD_FOLDER = 'photos'

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
    orient = img.resize(target_width = 640, target_height = 480, thumbnail = True)
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
    logging.info(f"angle = {frm.orientation()}")

def rotate(direction):
    frm = Frame()
    if direction == "H":
        angle = Orientation.HORIZONTAL
    elif direction == "V":
        angle = Orientation.VERTICAL
    frm.rotate(angle)

def add(file_path, file_description):
    logging.info(f"start processing file {file_path}")
    logging.info(f"description: {file_description}")
    path = Path(file_path)
    original_filename = path.stem
    target_path = Path(UPLOAD_FOLDER) / f"{uuid4().__str__()}{path.suffix}"
    logging.info(f"original_filename {original_filename}")
    logging.info(f"target path {target_path}")
    shutil.copy2(file_path, target_path) #replace with shutil.move

    img = Photo(
        image_path = target_path, 
        filename = original_filename, 
        description = file_description)

    exif_data = img.get_exif()
    logging.info(f'Get EXIF data: {exif_data}')
    logging.info('Generate thumbnail')
    img.resize(target_width = 640, target_height = 480, thumbnail = True)
    logging.info('Resize image')
    img.resize()
    logging.info('Add to database')
    album = PhotoAlbum()
    album.add(img)
    #print('Processing finished!')
    #print(exif_data)
    #print(img_orientation)

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
    parser.add_argument('-rotate', type=str, help='Rotate frame')
    parser.add_argument('-add', type=str, help='Add picture to database')
    parser.add_argument('-initdb', action='store_true', help='Initialise database')
    parser.add_argument('-listdb', action='store_true', help='List database')

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
    elif args.add:
        add(args.f,args.add)
    elif args.initdb:
        initdb()
    elif args.listdb:
        album = PhotoAlbum()
        album.list_all()
    else:
        parser.print_help()

    logging.info('END')

if __name__ == "__main__":
    main()

