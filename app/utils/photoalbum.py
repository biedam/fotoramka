from peewee import SqliteDatabase, Model, CharField, IntegerField, fn
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
    Filename = CharField()                         # photo filename
    Thumbnail = CharField()                        # thumbnail filename
    Photo_description = TextField(null=True)       # Optional text description
    LongDate = TextField(null=True)                # 
    ShortDate = TextField(null=True)               # 
    Country = TextField(null=True)                 # 
    Location = TextField(null=True)                # 
    Orientation = IntegerField(null=True)          # EXIF orientation value (enum)
    Active = IntegerField(null=True)               # for future use

    class Meta:
        database = db


class PhotoAlbum:
    def add(self, photo, description = ""):
        # Get current max sort_order (returns None if DB is empty)
        cur_photo_index = PhotoData.select(fn.MAX(PhotoData.Photo_order)).scalar() or 0
        
        PhotoData.create(
            Photo_order = cur_photo_index + 1,
            Filename = photo.image_path,
            Thumbnail = photo.thumb_path,
            Photo_description = description,
            LongDate = photo.exif['LongDate'],
            ShortDate = photo.exif['ShortDate'],
            Country = photo.exif['Country'],
            Location = photo.exif['Location'],
            Orientation = photo.orientation,
            Active = 1
        )


    #def remove():

    #def list_all():

    #def next_photo():

    #def random_photo():