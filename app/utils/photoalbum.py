from peewee import SqliteDatabase, Model, CharField, IntegerField, TextField, fn
from pathlib import Path
from utils.photo import Photo, Orientation
import logging

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'photos'
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


    #def remove():

    def list_all(self):
        total_images = PhotoData.select().count()
        logging.info(f"Total images in DB: {total_images}")
        images = [img for img in PhotoData.select().order_by(PhotoData.Photo_order)]
        #for image in ImageData.select().order_by(ImageData.sort_order):
        logging.info("List of images with original filename")
        print("=====================================")
        for image in images:
            print(f"{image.Photo_order}: {image.Original_filename}")
        print("=====================================")
        logging.info("Database dump")
        print("=====================================")
        for image in images:
            print(f"{image.Photo_order}: {image.Original_filename}, {image.Resized_path}, {image.Photo_description}" +
            f", {image.LongDate}, {image.Country}, {Orientation(image.Orientation)}")
        print("=====================================")
    #def next_photo():

    #def random_photo():