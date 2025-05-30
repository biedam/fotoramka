from flask import Flask, render_template, request, jsonify, redirect
from pathlib import Path
import os
from utils.photo import Photo
from utils.frame import Frame
from utils.photoalbum import PhotoAlbum
from uuid import uuid4
import threading
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s', level=logging.INFO)


app = Flask(__name__)

UPLOAD_FOLDER = 'static/photos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set max upload size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

#enable debug
app.config['PROPAGATE_EXCEPTIONS'] = True

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

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
    album = PhotoAlbum()
    album.add(img)


@app.route('/')
def index():
    album = PhotoAlbum()
    images = album.list_all()
    thumbnails = [image.Thumbnail_path for image in images]
    image_ids = [image.id for image in images]
    descriptions = [f"{image.Photo_description}, {image.Country}, {image.ShortDate}" for image in images]
    image_paths = [Path(thumbnail).relative_to("static") for thumbnail in thumbnails]
    
    
    print(image_paths)
    return render_template(
        '/index.html', 
        len = len(images), 
        image_paths = image_paths,
        image_ids = image_ids,
        descriptions = descriptions)
    #return 'To jest test serwera fotoramki'

@app.route('/dodaj')
def add_photo():
    return render_template('/dodaj.html')

@app.route('/ustawienia')
def settings():
    return render_template('/ustawienia.html')

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
    album = PhotoAlbum()
    frm = Frame()
    photo = album.get_byid(image_id)
    photo.set_palette(photo.PALETTE2)
    #photo.dither(90)
    angle = photo.orientation
    #thread_1 = threading.Thread(target=photo.display, args=(photo.processing_path,))
    thread_1 = threading.Thread(target=photo.display, args=())
    thread_2 = threading.Thread(target=frm.rotate, args=(angle,))
    thread_1.start()
    thread_2.start()

    # Optionally: redirect to a page showing full image
    return redirect('/')

@app.route('/delete_image', methods=['POST'])
def delete_image():
    #not yet implemented
    return redirect('/')


if __name__ == '__main__':
    #app.run(debug=True, port=80, host='0.0.0.0')
    app.run(debug=True, host='0.0.0.0')


