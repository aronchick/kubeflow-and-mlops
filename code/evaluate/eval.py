import json
import time
import requests
import argparse
import datetime
import numpy as np
from PIL import Image
from io import BytesIO
from pathlib import Path
import tensorflow as tf

global model

def info(msg, char = "#", width = 75):
    print("")
    print(char * width)
    print(char + "   %0*s" % ((-1*width)+5, msg) + char)
    print(char * width)

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

def load(path):
    global model

    print('Attempting to load model')
    model = tf.keras.models.load_model(path)
    model.summary()
    print('Done!')

    return model

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='sanity check on model')
    parser.add_argument('-b', '--base_path', help='directory to base data', default='../../data')
    parser.add_argument('-m', '--model', help='directory to training and test data', default='model/latest.h5')
    parser.add_argument('-v', '--val_path', help='validation path for scoring', default='val')
    args = parser.parse_args()

    model_path = str(Path(args.base_path).resolve().joinpath(args.model).resolve())
    

    # python score.py -m model/latest.h5