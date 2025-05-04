from flask import Flask, render_template, request, jsonify
from pathlib import Path
import os
from utils.photo import Photo
from utils.frame import Frame
import threading


app = Flask(__name__)
UPLOAD_FOLDER = 'photos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set max upload size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

#enable debug
app.config['PROPAGATE_EXCEPTIONS'] = True

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(file_path):
    print('Start processing ...')
    img = Photo(file_path)
    print('Get EXIF ...')
    exif_data = img.get_exif()
    print('crop, reorient, scale')
    img_orientation = img.resize(file_path)
    print('Processing finished!')
    print(exif_data)
    print(img_orientation)

@app.route('/')
def index():
    return render_template('/index.html')
    #return 'To jest test serwera fotoramki'

@app.route('/dodaj')
def add_photo():
    return render_template('/dodaj.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    description = request.form.get('description', '')
    print(description)
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'message': 'File type not allowed'}), 400

    file_path = Path(app.config['UPLOAD_FOLDER']) / file.filename
    file.save(file_path)

    # Process uploaded file
    thread = threading.Thread(target=process_file, args=(file_path,))
    thread.start()
    print('File uploaded successfully, processing in the background')

    return jsonify({'message': 'File uploaded successfully', 'description': description})





if __name__ == '__main__':
    #app.run(debug=True, port=80, host='0.0.0.0')
    app.run(debug=True, host='0.0.0.0')


