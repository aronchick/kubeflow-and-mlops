import json
import time
import requests
import datetime
import numpy as np
from PIL import Image
from io import BytesIO
import tensorflow as tf

from azureml.core.model import Model

def init():
    global model

    try:
        model_path = Model.get_model_path('dogsandcats')
    except:
        model_path = 'latest.h5'

    print('Attempting to load model')
    model = tf.keras.models.load_model(model_path)
    model.summary()
    print('Done!')

    print('Initialized model "{}" at {}'.format(model_path, datetime.datetime.now()))

def run(raw_data):
    global model
    info('Inference')
    prev_time = time.time()
          
    post = json.loads(raw_data)
    img_path = post['image']

    current_time = time.time()

    tensor = process_image(img_path, 160)
    t = tf.reshape(tensor, [-1, 160, 160, 3])
    o = model.predict(t, steps=1)[0][0]
    inference_time = datetime.timedelta(seconds=current_time - prev_time)

    payload = {
        'time': inference_time.total_seconds(),
        'prediction': 'Cat' if o < 0 else 'Dog',
        'scores': o
    }

    print('Input ({}), Prediction ({})'.format(post['image'], payload))

    return payload

def process_image(path, image_size):
    # Extract image (from web or path)
    if(path.startswith('http')):
        response = requests.get(path)
        img = np.array(Image.open(BytesIO(response.content)))
    else:
        img = np.array(Image.open(path))

    img_tensor = tf.convert_to_tensor(img, dtype=tf.float32)
    img_final = tf.image.resize_image_with_pad(img_tensor, image_size, image_size) / 255
    return img_final

def info(msg, char = "#", width = 75):
    print("")
    print(char * width)
    print(char + "   %0*s" % ((-1*width)+5, msg) + char)
    print(char * width)

if __name__ == "__main__":
    images = {
        'cat': 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131',
        'dog': 'https://images.pexels.com/photos/356378/pexels-photo-356378.jpeg'
    }

    init()

    for k, v in images.items():
        print('{} => {}'.format(k, v))

    run(json.dumps({ 'image': images['cat'] }))
    run(json.dumps({ 'image': images['dog'] }))