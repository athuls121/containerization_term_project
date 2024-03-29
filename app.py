from flask import Flask
from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH
from pywebio.input import file_upload, input
from pywebio.output import put_markdown, put_table, put_image
from PIL import Image
import os
import redis
import base64
import pickle

app = Flask(__name__)

## Connect to Redis
redis_host = 'redis' #service name for Docker_Swarm
redis_port = 6379
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

def save_image_metadata(image_key, metadata):
    # Save metadata to Redis
    metadata_pickled = pickle.dumps(metadata)
    redis_client.set(image_key, metadata_pickled)

def image_metadata(file_path):
    image = Image.open(file_path)
    metadata = {
        'Filename': os.path.basename(file_path),
        'Format': image.format,
        'Mode': image.mode,
        'Size': f'{image.width} x {image.height}',
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

app.add_url_rule('/', 'webio_view', webio_view(app_func), methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
