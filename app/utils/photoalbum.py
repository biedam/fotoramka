from peewee import SqliteDatabase, Model, CharField, IntegerField, TextField, fn
from pathlib import Path
from utils.photo import Photo, Orientation
import logging
import os

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'static/photos'
DB_NAME = 'photos.db'

db_path = Path(UPLOAD_FOLDER) / DB_NAME

# Connect to SQLite DB
db = SqliteDatabase(db_path)


# Define model
class PhotoData(Model):
    Photo_order = IntegerField(default=0)          # order of the displayed photos
    Original_filename = CharField()                # original filename
    Resized_path = CharField()                     # photo path
    Thumbnail_path = CharField()                   # thumbnail path
    Photo_description = TextField(null=True)       # Optional text description
    LongDate = TextField(null=True)                # 
    ShortDate = TextField(null=True)               # 
    Country = TextField(null=True)                 # 
    Location = TextField(null=True)                # 
    Orientation = IntegerField(null=True)          # EXIF orientation value (enum)
    Active = IntegerField(null=True)               # for future use

    class Meta:
        database = db

def initdb():
    db.connect()
    db.create_tables([PhotoData])



class PhotoAlbum:
    def add(self, photo):
        # Get current max sort_order (returns None if DB is empty)
        cur_photo_index = PhotoData.select(fn.MAX(PhotoData.Photo_order)).scalar() or 0
        
        PhotoData.create(
            Photo_order = cur_photo_index + 1,
            Original_filename = photo.filename,
            Resized_path = photo.image_path,
            Thumbnail_path = photo.thumb_path,
            Photo_description = photo.description,
            LongDate = photo.exif['LongDate'],
            ShortDate = photo.exif['ShortDate'],
            Country = photo.exif['Country'],
            Location = photo.exif['Location'],
            Orientation = photo.orientation.value,
            Active = 1
        )

    def remove(self, image_id):
        #image = PhotoData.get_by_id(image_id)
        #
        try:
            image = PhotoData.get_by_id(image_id)
            if os.path.isfile(image.Resized_path):
                os.remove(image.Resized_path)
            if os.path.isfile(image.Thumbnail_path):
                os.remove(image.Thumbnail_path)

            image.delete_instance()
            logging.info(f"image with ID {image_id} deleted")
        except ImageData.DoesNotExist:
            logging.warning(f"Image id {image_id} not in database")
        #delete also files from disk

    def list_all(self):
        total_images = PhotoData.select().count()
        logging.info(f"Total images in DB: {total_images}")
        images = [img for img in PhotoData.select().order_by(PhotoData.Photo_order)]
        return images

    def get_byid(self, image_id):
        #image = PhotoData.get_by_id(image_id)
        #image = ImageData.get(ImageData.filename == "photo.jpg")
        try:
            image = PhotoData.get_by_id(image_id)
            photo = Photo(
                image_path = image.Resized_path,
                filename = image.Original_filename, 
                description = image.Photo_description)
            
            photo.thumb_path = image.Thumbnail_path
            photo.exif = {
                "LongDate": image.LongDate,
                "ShortDate": image.ShortDate,
                "Country": image.Country,
                "Location": image.Location
            }
            photo.orientation = Orientation(image.Orientation)

            return photo
        except PhotoData.DoesNotExist:
            logging.warning(f"Image id {image_id} not in database")
            return None

    #def next_photo():

    #def random_photo():
