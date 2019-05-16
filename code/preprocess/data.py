import os
import time
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path

def process_image(path, image_size):
    img_raw = tf.io.read_file(path)
    img_tensor = tf.image.decode_jpeg(img_raw, channels=3)
    img_final = tf.image.resize_image_with_pad(img_tensor, image_size, image_size) / 255
    return img_final

def walk_images(base_path, image_size=160):
    images = []
    print('Scanning {}'.format(base_path))
    # find subdirectories in base path
    # (they should be the labels)
    labels = []
    for (_, dirs, _) in os.walk(base_path):
        print('Found {}'.format(dirs))
        labels = dirs
        break

    for d in labels:
        path = os.path.join(base_path, d)
        print('Processing {}'.format(path))
        # only care about files in directory
        for item in os.listdir(path):
            if not item.endswith('.jpg'):
                print('\nskipping {}'.format(item))
                continue

            image = os.path.join(path, item)
            print(image)
            try:
                img = process_image(image, image_size)
                assert img.shape[2] == 3, "Invalid channel count"
                # write out good images
                images.append(image)
            except Exception as e:
                print('\n{}\n{}\n'.format(e, image))

    return images

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='data cleaning for binary image task')
    parser.add_argument('-b', '--base_path', help='directory to base data', default='..')
    parser.add_argument('-d', '--data', help='directory to training and test data', default='data')
    parser.add_argument('-t', '--target', help='target file to hold good data', default='dataset.txt')
    parser.add_argument('-i', '--img_size', help='target image size to verify', default=160, type=int)
    args = parser.parse_args()

    print('Using TensorFlow v.{}'.format(tf.__version__))
    
    base_path = Path(args.base_path).joinpath(args.data).resolve()
    target_path = Path(base_path).resolve().joinpath(args.target)

    images = walk_images(str(base_path), args.img_size)

    # save file
    print('writing dataset to {}'.format(target_path))
    with open(str(target_path), 'w+') as f:
        f.write('\n'.join(images))

    # python data.py -d data/PetImages -t dataset.txt
