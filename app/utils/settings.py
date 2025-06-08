from peewee import Model, CharField, SqliteDatabase
from pathlib import Path

SETTINGS_FOLDER = 'static/photos'
SETTINGS_DB_NAME = 'settings.db'

db_path = Path(SETTINGS_FOLDER) / SETTINGS_DB_NAME

# Connect to SQLite DB
db = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = db

class Setting(BaseModel):
    key = CharField(unique=True)
    value = CharField(null=True)

# Wstępna inicjalizacja bazy
def init_setting():
    db.connect()
    db.create_tables([Setting], safe=True)

def get_setting(key, default=None):
    setting = Setting.get_or_none(Setting.key == key)
    return setting.value if setting else default

def set_setting(key, value):
    setting, created = Setting.get_or_create(key=key)
    setting.value = value
    setting.save()