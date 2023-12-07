from flask import Flask
from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH
from pywebio.input import *
from pywebio.output import *
from PIL import Image
import os
import redis
import base64
import pickle

app = Flask(__name__)

# Connect to Redis
#redis_host = '10.26.128.158'
redis_host = 'my-redis-service'
redis_port = 6379
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

def save_image_metadata(image_key, metadata):
    # Save metadata to Redis
    metadata_pickled = pickle.dumps(metadata)
    redis_client.set(image_key, metadata_pickled)

def get_image_metadata(image_key):
    # Retrieve metadata from Redis
    metadata_pickled = redis_client.get(image_key)
    if metadata_pickled:
        return pickle.loads(metadata_pickled)
    return None

def image_metadata(file_path):
    image = Image.open(file_path)
    metadata = {
        'Filename': os.path.basename(file_path),
        'Format': image.format,
        'Mode': image.mode,
        'Size': f'{image.width} x {image.height}',
        'DPI (dots per inch)': image.info.get('dpi'),
        'Bits per channel': image.info.get('bits'),
        'Color space': image.info.get('icc_profile'),
        'Orientation': image.info.get('exif'),
        'Camera Make': image.info.get('make'),
        'Camera Model': image.info.get('model'),
        'Software': image.info.get('software'),
        'Date Taken': image.info.get('datetime'),
        'Exposure Time': image.info.get('exposuretime'),
        'Focal Length': image.info.get('focallength'),
        'Aperture': image.info.get('aperture'),
        'ISO': image.info.get('iso'),
    }
    return metadata

def app_func():
    put_markdown("## MetaSnap - Image Metadata Viewer")

    file_info = file_upload("Upload an image:")
    image_path = os.path.join(STATIC_PATH, file_info['filename'])
    with open(image_path, 'wb') as f:
        f.write(file_info['content'])

    metadata = image_metadata(image_path)

    # Generate a unique key for each image
    image_key = f"image:{file_info['filename']}"

    # Save metadata to Redis
    save_image_metadata(image_key, metadata)

    put_markdown("### Image Metadata:")
    put_table(list(metadata.items()))

    # Display the uploaded image
    img_content = base64.b64encode(open(image_path, 'rb').read()).decode()
    put_image(img_content, width="50%", height="50%")

    # Save the image key in the session for future retrieval
    session['image_key'] = image_key

app.add_url_rule('/', 'webio_view', webio_view(app_func), methods=['GET', 'POST'])

if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=80)
    app.run(debug=False, port=80)
