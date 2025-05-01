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

class Orientation(Enum):
    HORIZONTAL = 1
    VERTICAL = 2

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
        print("exif start")
        with Image.open(self.image_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                print("no exif data")
                return {}
            exif = {}
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                exif[decoded] = value
            
            gps_info = {}
            if "GPSInfo" in exif:
                for key, val in exif["GPSInfo"].items():
                    gps_info[GPSTAGS.get(key, key)] = val
            
            # Extract coordinates if available
            latitude = None
            longitude = None
            country = None
            photo_location = None
            if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
                lat_vals = gps_info["GPSLatitude"]
                lon_vals = gps_info["GPSLongitude"]
                lat_ref = gps_info.get("GPSLatitudeRef", "N")
                lon_ref = gps_info.get("GPSLongitudeRef", "E")
                
                latitude = (lat_vals[0] + lat_vals[1] / 60 + lat_vals[2] / 3600) * (-1 if lat_ref == "S" else 1)
                longitude = (lon_vals[0] + lon_vals[1] / 60 + lon_vals[2] / 3600) * (-1 if lon_ref == "W" else 1)
                
                # Reverse geocode to get country name
                location = rg.search((latitude, longitude))
                country_code = location[0]['cc'] if location else None
                photo_location = location[0]['admin1'] if location else None

                # ✅ Convert country code to full name
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

            return {
                "LongDate": long_date,
                "ShortDate": short_date,
                "Country": country_name,
                "Location": photo_location
            }

    def resize(self, out_path=None, jpg_quality=95):
        #resize and crop to 2:3 aspect ratio
        print("resize start")
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
                print(f"Could not handle EXIF orientation: {e}")

            orientation = none
            width, height = img.size
            #preserve EXIF data
            exif = img.info['exif']
            print(img.size)
            target_width = 1600
            target_height = 1200
            if width > height: # horizontal photo
                orientation = Orientation.HORIZONTAL
                # preserve aspcect ratio
                new_height = target_height
                new_width = int((width / height) * target_height)

                # prepare to crop left&right if needed
                top = 0
                bottom = new_height
                left = (new_width - target_width) / 2
                right = (new_width + target_width) / 2
                
            else: # vertical photo
                orientation = Orientation.VERTICAL
                # preserve aspcect ratio & swith width and heigth
                new_width = target_height
                new_height = int((height / width) * target_height)
                
                # prepare to crop top&bottom if needed
                # height & width are switched for vertical photos
                top = (new_height - target_width) / 2
                bottom = (new_height + target_width) / 2
                left = 0
                right = new_width

            print((new_width, new_height))
            # resize
            img = img.resize((new_width, new_height), Image.LANCZOS)
            # crop
            img = img.crop((left, top, right, bottom))

            if out_path is not None:
                img.save(out_path, quality=jpg_quality)
            else:
                img.save(self.image_paht, quality=jpg_quality)

            return orientation