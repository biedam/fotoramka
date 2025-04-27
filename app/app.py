from flask import Flask, render_template, request, jsonify
import os
import reverse_geocoder as rg
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def resize_image(image_path):
    print("resize start")
    with Image.open(image_path) as img:
        width, height = img.size
        target_width = 1600
        target_height = 1200
        if width > height:
            new_width = target_width
            new_height = int((height / width) * target_width)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        else:
            new_width = int((width / height) * target_height)
            new_height = target_height
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Crop the image to 1600x1200 if needed
        left = (new_width - target_width) / 2
        top = (new_height - target_height) / 2
        right = (new_width + target_width) / 2
        bottom = (new_height + target_height) / 2
        img = img.crop((left, top, right, bottom))
        img.save(image_path)

def get_exif_data(image_path):
    print("exif start")
    with Image.open(image_path) as img:
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
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat_vals = gps_info["GPSLatitude"]
            lon_vals = gps_info["GPSLongitude"]
            lat_ref = gps_info.get("GPSLatitudeRef", "N")
            lon_ref = gps_info.get("GPSLongitudeRef", "E")
            
            latitude = (lat_vals[0] + lat_vals[1] / 60 + lat_vals[2] / 3600) * (-1 if lat_ref == "S" else 1)
            longitude = (lon_vals[0] + lon_vals[1] / 60 + lon_vals[2] / 3600) * (-1 if lon_ref == "W" else 1)
            
            # Reverse geocode to get country name
            location = rg.search((latitude, longitude))
            country = location[0]['cc'] if location else None
        
        print("EXIF Data:", {"DateTime": exif.get("DateTime"), "Latitude": latitude, "Longitude": longitude, "Country": country})
        
        return {
            "DateTime": exif.get("DateTime"),
            "Latitude": latitude,
            "Longitude": longitude,
            "Country": country
        }

app = Flask(__name__)
UPLOAD_FOLDER = 'zdjecia'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set max upload size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

#enable debug
app.config['PROPAGATE_EXCEPTIONS'] = True

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Extract EXIF data
    exif_data = get_exif_data(file_path)

    # Resize image
    resize_image(file_path)
    


    return jsonify({'message': 'File uploaded successfully', 'description': description})





if __name__ == '__main__':
    #app.run(debug=True, port=80, host='0.0.0.0')
    app.run(debug=True, host='0.0.0.0')