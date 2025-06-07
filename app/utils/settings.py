from peewee import Model, CharField, SqliteDatabase

SETTINGS_FOLDER = 'static/photos'
SETTINGS_DB_NAME = 'settings.db'

class BaseModel(Model):
    class Meta:
        database = db

class Setting(BaseModel):
    key = CharField(unique=True)
    value = CharField()

# Wstępna inicjalizacja bazy
def init_db():
    db.connect()
    db.create_tables([Setting], safe=True)

def get_setting(key, default=None):
    setting = Setting.get_or_none(Setting.key == key)
    return setting.value if setting else default

def set_setting(key, value):
    setting, created = Setting.get_or_create(key=key)
    setting.value = value
    setting.save()