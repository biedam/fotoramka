#=============================================================================
#============================ FOTORAMKA project ==============================
#=============================================================================
# author            : biedam
# notes             : 
# license           : MIT
#=============================================================================


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
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import reverse_geocoder as rg
import pycountry
from babel.dates import format_datetime
from babel import Locale
from datetime import datetime
from enum import Enum
from epd_drv import epd13in3E
import logging

logger = logging.getLogger(__name__)

class Orientation(Enum):
    HORIZONTAL = 1
    VERTICAL = 2

epd = epd13in3E.EPD()

PALETTE_VAL1 = (0,0,0,  255,255,255,  255,255,0,  255,0,0,  0,0,0,  0,0,255,  0,255,0) + (0,0,0)*249
PALETTE_VAL2 = (0,0,0,  255,255,255,  244,244,0,  126,10,28,  0,0,0,  75,66,189,  68,145,66) + (0,0,0)*249

utils_dir = Path(__file__).parent
PALETTE_FILE1 = utils_dir / "palette.bmp"
PALETTE_FILE2 = utils_dir / "palette3.bmp"



class Photo:
    #RGB palette
    PALETTE1 = (PALETTE_VAL1, PALETTE_FILE1)
    #Calibrated palette
    PALETTE2 = (PALETTE_VAL2, PALETTE_FILE2)
    

    def __init__(self, image_path, filename = "", description = ""):
        self.image_path = image_path
        #utils_dir = Path(__file__).parent
        self.processing_path = "img.png"
        self.palette = None
        self.filename = filename
        self.description = description

    def set_palette(self, palette):
        self.palette = palette

    def dither(self, diffusion):
        diffusion_amount = f"dither:diffusion-amount={diffusion}%"
        dither_palette = f"{self.palette[1]}"
        dither_command = ['convert', self.image_path, '-dither', 'FloydSteinberg', '-define', diffusion_amount, '-remap', dither_palette, '-type', 'truecolor', self.processing_path]
        subprocess.run(dither_command, check=True)

    def annotate(self, position, font_size, text):
        file_in = self.image_path
        file_out = self.processing_path
        font = "Excalifont-Regular"
        partial_cmd = ['-gravity', position, '-font', font, '-pointsize', f'{font_size}', '-annotate', '0', text]
        annotation_command = ['convert', file_in, '-strokewidth', '5', '-stroke', 'black'] + partial_cmd + ['-fill', 'white', '-strokewidth', '1', '-stroke', 'white'] + partial_cmd + [file_out]
        subprocess.run(annotation_command, check=True)

    polish_months_nominative = {
    1: "styczeń",
    2: "luty",
    3: "marzec",
    4: "kwiecień",
    5: "maj",
    6: "czerwiec",
    7: "lipiec",
    8: "sierpień",
    9: "wrzesień",
    10: "październik",
    11: "listopad",
    12: "grudzień"
    }

    def get_exif(self):
        logger.info("exif start")
        with Image.open(self.image_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                logger.info("no exif data")
                self.exif = {
                    "LongDate": None,
                    "ShortDate": None,
                    "Country": None,
                    "Location": None,
                    "Date": None
                }
                return self.exif
            exif = {}
            logger.debug("get exif data")
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                exif[decoded] = value
            
            logger.debug("get gps info")
            gps_info = {}
            if "GPSInfo" in exif:
                for key, val in exif["GPSInfo"].items():
                    gps_info[GPSTAGS.get(key, key)] = val
            
            logger.debug(gps_info)
            # Extract coordinates if available
            latitude = None
            longitude = None
            country = None
            photo_location = None
            if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
                lat_vals = gps_info["GPSLatitude"]
                lon_vals = gps_info["GPSLongitude"]
                logger.debug(f"gps info {lat_vals}, {lon_vals}")
                lat_ref = gps_info.get("GPSLatitudeRef", "N")
                lon_ref = gps_info.get("GPSLongitudeRef", "E")
                
                latitude = (lat_vals[0] + lat_vals[1] / 60 + lat_vals[2] / 3600) * (-1 if lat_ref == "S" else 1)
                longitude = (lon_vals[0] + lon_vals[1] / 60 + lon_vals[2] / 3600) * (-1 if lon_ref == "W" else 1)
                
                # Reverse geocode to get country name
                logger.debug(f"reverse geocode {latitude}, {longitude}")
                try: 
                    location = rg.search((latitude, longitude))
                except:
                    logger.debug(f"No valid GPS data")
                    location = None

                country_code = location[0]['cc'] if location else None
                photo_location = location[0]['admin1'] if location else None

                # ✅ Convert country code to full name
                logger.debug("convert country code to full name")
                try:
                    country = pycountry.countries.get(alpha_2=country_code)
                    if country:
                        #country_name = country.name if country else None
                        locale_pl = Locale('pl')
                        country_name = locale_pl.territories.get(country.alpha_2, country.name)
                    else:
                        country_name = country_code
                except:
                    country_name = country_code
            
            # ✅ Format date in Polish
            date_string = exif.get("DateTime")  # format: "2025:05:01 14:32:00"
            readable_date = None
            if date_string:
                dt = datetime.strptime(date_string, "%Y:%m:%d %H:%M:%S")
                long_date = format_datetime(dt, "d MMMM y", locale='pl_PL')
                month_name = self.polish_months_nominative[dt.month]
                short_date = f"{month_name} {dt.year}"

            self.exif = {
                "LongDate": long_date,
                "ShortDate": short_date,
                "Country": country_name,
                "Location": photo_location,
                "Date": date_string
            }

            return self.exif

    def resize(self, out_path=None, jpg_quality=95, target_width = 1600, target_height = 1200, thumbnail = False):
        # resolution for thumbnails can be 320 x 240
        # resize and crop to 2:3 aspect ratio
        logging.info("Resize image")
        with Image.open(self.image_path) as img:
            # Handle orientation from EXIF
            try:
                exif = img._getexif()
                if exif is not None:
                    for tag, value in exif.items():
                        decoded = TAGS.get(tag, tag)
                        if decoded == "Orientation":
                            orientation = value
                            if orientation == 3:
                                img = img.rotate(180, expand=True)
                            elif orientation == 6:
                                img = img.rotate(270, expand=True)
                            elif orientation == 8:
                                img = img.rotate(90, expand=True)
                            break
            except Exception as e:
                logging.error(f"Could not handle EXIF orientation: {e}")

            if thumbnail == False:
                self.orientation = None
            width, height = img.size
            #preserve EXIF data
            #exif = img.info['exif']
            print(img.size)
            
            if width > height: # horizontal photo
                _orientation = Orientation.HORIZONTAL
                # preserve aspcect ratio
                new_height = target_height
                new_width = int((width / height) * target_height)

                # prepare to crop left&right if needed
                top = 0
                bottom = new_height
                left = (new_width - target_width) / 2
                right = (new_width + target_width) / 2
                
            else: # vertical photo
                _orientation = Orientation.VERTICAL
                # preserve aspcect ratio & swith width and heigth
                new_width = target_height
                new_height = int((height / width) * target_height)
                
                # prepare to crop top&bottom if needed
                # height & width are switched for vertical photos
                top = (new_height - target_width) / 2
                bottom = (new_height + target_width) / 2
                left = 0
                right = new_width

            logging.info((new_width, new_height))
            # resize
            img = img.resize((new_width, new_height), Image.LANCZOS)
            # crop
            img = img.crop((left, top, right, bottom))

            
            if out_path is not None:
                logging.info(f"saving resized image {out_path}")
                img.save(out_path, quality=jpg_quality)
                if thumbnail == True:
                    self.thumb_path = out_path
            else:
                if thumbnail == False:
                    logging.info(f"saving resized image {self.image_path}")
                    img.save(self.image_path, quality=jpg_quality)
                else:
                    image_path = Path(self.image_path)
                    self.thumb_path = image_path.with_name(f"{image_path.stem}_thumb{image_path.suffix}")
                    logging.info(f"saving resized image {self.thumb_path}")
                    img.save(self.thumb_path, quality=jpg_quality)

            if thumbnail == False:
                self.orientation = _orientation
            return _orientation

    def display(self, path=None):
        if path == None: 
            path = self.image_path
        try:
            epd.Init()
            logging.info("Clearing framebuffer")

            # Drawing on the image
            image = Image.new('RGB', (epd.width, epd.height), epd.WHITE)  # 255: clear the frame
            # read bmp file 
            logging.info("Read photo file")
            image = Image.open(path)
            pal_image = Image.new("P", (1,1))
            pal_image.putpalette(self.palette[0])
            logging.info("Set palette")
            # Check if we need to rotate the image
            imwidth, imheight = image.size
            print(imwidth)
            if(imwidth == epd.width and imheight == epd.height):
                image_temp = image
            elif(imwidth == epd.height and imheight == epd.width):
                image_temp = image.rotate(90, expand=True)
            else:
                logging.error("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, epd.width, epd.height))

            # Convert the soruce image to the 7 colors, dithering if needed
            image_7color = image_temp.convert("RGB").quantize(palette=pal_image)
            buf_7color = bytearray(image_7color.tobytes('raw'))

            # PIL does not support 4 bit color, so pack the 4 bits of color
            # into a single byte to transfer to the panel
            buf = [0x00] * int(epd.width * epd.height / 2)
            idx = 0
            for i in range(0, len(buf_7color), 2):
                buf[idx] = (buf_7color[i] << 4) + buf_7color[i+1]
                idx += 1

            epd.display(buf)
            time.sleep(3)


            logging.info("goto sleep...")
            epd.sleep()
        except:
            logging.info("goto sleep...")
            epd.sleep()
    def clear(self):
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