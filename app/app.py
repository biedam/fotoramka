from flask import Flask, render_template, request, jsonify, redirect, flash
from pathlib import Path
import os
from utils.photo import Photo
from utils.frame import Frame
from utils.photoalbum import Album
from uuid import uuid4
import threading
import logging
from datetime import datetime as dt
from utils.settings import set_setting, get_setting, init_setting

#logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s', level=logging.INFO)
logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s', level=logging.DEBUG)


app = Flask(__name__)

UPLOAD_FOLDER = 'static/photos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set max upload size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

#enable debug
app.config['PROPAGATE_EXCEPTIONS'] = True

app.secret_key = b'some_secret_key'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

init_setting()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(img):
    app.logger.info('Start processing image')
    
    exif_data = img.get_exif()
    app.logger.info(f'Get EXIF data: {exif_data}')
    app.logger.info('Generate thumbnail')
    img.resize(target_width = 640, target_height = 480, thumbnail = True)
    app.logger.info('Resize image')
    img.resize()
    app.logger.info('Add to database')
    Album.add(img)

#================= Functions to display image ==================

def Generate_description(description, country, short_date, content = 'desc_date'):
    if content == 'desc_date':
        if country == None:
            if short_date == None:
                text = f"{description}"
            else:
                text = f"{description}, {short_date}"
        else:
            text = f"{description}, {country}, {short_date}"
    elif content == 'desc':
        text = description
    elif content == 'none':
        text = ''
    else:
        text = ''
    
    return text

display_lock = threading.Lock()

def display_photo_runner(photo):
    app.logger.info('Start display photo')
    with display_lock:
        photo.display(photo.processing_path)
        app.logger.info('End display photo')

def display_photo(photo):
    app.logger.info(f"Displaying photo: {photo.image_path}")
    print(f"[{dt.now()}] Displaying photo: {photo.image_path}, {photo.description}")
    photo.set_palette(photo.PALETTE2)
    frm = Frame()
    #photo.dither(90)
    angle = photo.orientation
    text = Generate_description(
        photo.description,photo.exif['Country'],
        photo.exif['ShortDate'],
        get_setting('opis', ''))
    app.logger.info(f"Annotating image with text: {text}")        
    #text = f"{photo.description}, {photo.exif['Country']}, {photo.exif['ShortDate']}"
    photo.annotate('South',40,text)
        #thread_1 = threading.Thread(target=photo.display, args=(photo.processing_path,))
    thread_1 = threading.Thread(target=display_photo_runner, args=(photo,))
    thread_2 = threading.Thread(target=frm.rotate, args=(angle,))
    thread_1.start()
    thread_2.start()

#================= Display scheduler functions ==================
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

scheduler = BackgroundScheduler()

def scheduled_image_update():
    app.logger.info('==============================')
    app.logger.info('Scheduled Image update')
    app.logger.info('==============================')
    print(f"[{dt.now()}] Scheduled Image update")
    disp_setting = get_setting('disp', '')

    if disp_setting == 'random':
        app.logger.info('display rantom photo')
        photo = Album.get_random()
        display_photo(photo)
    else:
        app.logger.info('no photo change')

    

scheduler.add_job(
    scheduled_image_update, 
    'cron', 
    hour='0,12', 
    minute=0, 
    id='image_update', 
    replace_existing=True)

def scheduler_update(freq):

    if freq == '1':
        hours = '0'
    elif freq == '2':
        hours = '0,12'
    elif freq == '4':
    # do not update photo at night time (0AM - 6AM)
        hours = '0,12,18'

    try:
        job_id ='image_update'
        scheduler.reschedule_job(job_id, trigger='cron', hour=hours, minute=52 )
        app.logger.info(f"Scheduler rescheduled to following hours: {hours}")
    except Exception as e:
        return app.logger.error(str(e))

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'added_asc')
    if sort_by == 'added_asc':
        images = Album.list_all(order_by='id', asc=True)
    elif sort_by == 'date_asc':
        images = Album.list_all(order_by='date', asc=True)
    elif sort_by == 'date_desc':
        images = Album.list_all(order_by='date', asc=False)
    elif sort_by == 'added_desc':
        images = Album.list_all(order_by='id', asc=False)
    else:  
        images = Album.list_all()
    
    thumbnails = [image.Thumbnail_path for image in images]
    image_ids = [image.id for image in images]
    descriptions = []
    for image in images:
        descriptions.append(Generate_description(image.Photo_description, image.Country, image.ShortDate))
    
    image_paths = [Path(thumbnail).relative_to("static") for thumbnail in thumbnails]
    
    #print(image_paths)
    return render_template(
        '/index.html', 
        len = len(images), 
        image_paths = image_paths,
        image_ids = image_ids,
        descriptions = descriptions,
        sort_by=sort_by)
    #return 'To jest test serwera fotoramki'

@app.route('/dodaj')
def add_photo():
    return render_template('/dodaj.html')

@app.route('/ustawienia', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        app.logger.info(f"Set settings: opis {request.form.get('opis')}")
        set_setting('opis', request.form.get('opis'))
        app.logger.info(f"Set settings: freq {request.form.get('freq')}")
        set_setting('freq', request.form.get('freq'))
        app.logger.info(f"Set settings: disp {request.form.get('disp')}")
        set_setting('disp', request.form.get('disp'))
        
        scheduler_update(get_setting('freq', ''))

        return redirect('/ustawienia')  # reload to GET after POST

    current_settings = {
        'opis': get_setting('opis', ''),
        'freq': get_setting('freq', ''),
        'disp': get_setting('disp', '')
    }

    return render_template(
        '/ustawienia.html',
        settings=current_settings)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'message': 'File type not allowed'}), 400

    app.logger.info(f"Start processing file {file.filename}, {description}")
    print(f"[{dt.now()}] Uploaded photo {file.filename}, {description}")
    original_path = Path(file.filename)
    target_path = Path(app.config['UPLOAD_FOLDER']) / f"{uuid4().__str__()}{original_path.suffix}"
    file.save(target_path)

    img = Photo(
        image_path = target_path, 
        filename = original_path.stem, 
        description = description)

    # Process uploaded file
    thread = threading.Thread(target=process_file, args=(img,))
    thread.start()
    app.logger.info('File uploaded successfully, processing in the background')

    return jsonify({'message': 'File uploaded successfully', 'description': description})

@app.route('/display_image', methods=['POST'])
def display_image():
    image_id = request.form['image_id']
    app.logger.info(f"Display image ID: {image_id}")
    #frm = Frame()
    photo = Album.get_byid(image_id)

    if(display_lock.locked()):
        flash("Fotoramka jest zajęta wyświetlaniem zdjęcia! Spróbuj później.")
    else:
        flash("Wyświetlanie zdjęcia...")
        display_photo(photo)

    return redirect('/')

@app.route('/delete_image', methods=['POST'])
def delete_image():
    image_id = request.form['image_id']
    app.logger.info(f"Deleting image ID: {image_id}")
    Album.remove(image_id)
    return redirect('/')



if __name__ == '__main__':
    #only run scheduler in the flask main process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    run_mode = os.environ.get('FLASK_RUN_MODE', 'development')
    app.logger.info(f"environment {run_mode}")
    if run_mode == 'production':
        app.run(host='0.0.0.0', port=80, debug=False)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
    #app.run(debug=True, host='0.0.0.0')


