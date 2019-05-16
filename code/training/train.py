from __future__ import absolute_import, division, print_function
import os
import math
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from random import shuffle
from datetime import datetime
from tensorflow.data import Dataset

global image_size

def info(msg, char = "#", width = 75):
    print("")
    print(char * width)
    print(char + "   %0*s" % ((-1*width)+5, msg) + char)
    print(char * width)

def check_dir(path, check=False):
    if check:
        assert os.path.exists(path), '{} does not exist!'.format(path)
    else:
        if not os.path.exists(path):
            os.makedirs(path)
        return Path(path).resolve()

def process_image(path, label):
    img_raw = tf.io.read_file(path)
    img_tensor = tf.image.decode_jpeg(img_raw, channels=3)
    img_final = tf.image.resize(img_tensor, [image_size, image_size]) / 255
    return img_final, label

def load_dataset(base_path, dataset, split=[8, 1, 1]):
    # normalize splits
    splits = np.array(split) / np.sum(np.array(split))

    # find labels - parent folder names
    labels = {}
    for (_, dirs, _) in os.walk(base_path):
        print('found {}'.format(dirs))
        labels = { k: v for (v, k) in enumerate(dirs) }
        print('using {}'.format(labels))
        break
        
    # load all files along with idx label
    print('loading dataset from {}'.format(dataset))
    with open(dataset, 'r') as d:
        data = [(str(Path(f.strip()).absolute()), labels[Path(f.strip()).parent.name]) for f in d.readlines()]

    print('dataset size: {}\nsuffling data...'.format(len(data)))
    
    # shuffle data
    shuffle(data)
    
    print('splitting data...')
    # split data
    train_idx = int(len(data) * splits[0])
    eval_idx = int(len(data) * splits[1])
    
    return data[:train_idx], \
            data[train_idx:train_idx + eval_idx], \
            data[train_idx + eval_idx:], \
            labels

#@print_info
def run(data_path, image_size=160, epochs=10, batch_size=32, learning_rate=0.0001, output='model', dataset=None):
    img_shape = (image_size, image_size, 3)

    info('Loading Data Set')
    # load dataset
    train, test, val, labels = load_dataset(data_path, dataset)

    # training data
    train_data, train_labels = zip(*train)
    train_ds = Dataset.zip((Dataset.from_tensor_slices(list(train_data)),
                            Dataset.from_tensor_slices(list(train_labels))))

    train_ds = train_ds.map(map_func=process_image, 
                            num_parallel_calls=5)

    train_ds = train_ds.apply(tf.data.experimental.ignore_errors())

    train_ds = train_ds.batch(batch_size)
    train_ds = train_ds.prefetch(buffer_size=5)
    train_ds = train_ds.repeat()

    # model
    info('Creating Model')
    base_model = tf.keras.applications.MobileNetV2(input_shape=img_shape,
                                               include_top=False, 
                                               weights='imagenet')
    base_model.trainable = False

    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer=tf.keras.optimizers.RMSprop(lr=learning_rate), 
              loss='binary_crossentropy', 
              metrics=['accuracy'])

    model.summary()

    # training
    info('Training')
    steps_per_epoch = math.ceil(len(train)/batch_size)
    history = model.fit(train_ds, epochs=epochs, steps_per_epoch=steps_per_epoch)

    info('Testing Model')
    print('TODO!')

    # save model
    info('Saving Model')
    
    # check existence of base model folder
    output = check_dir(output)

    print('Serializing into saved_model format')
    tf.saved_model.save(model, str(output))

    # add time prefix folder
    #stamp = datetime.now().strftime('%y_%m_%d_%H_%M.h5')
    #stamped = str(Path(output).joinpath(stamp))
    file_output = str(Path(output).joinpath('latest.h5'))
    #print('Serializing model to:\n{}\n{}'.format(stamped, output))
    model.save(file_output)
    #model.save(stamped)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='transfer learning for binary image task')
    parser.add_argument('-s', '--base_path', help='directory to base data', default='..')
    parser.add_argument('-d', '--data', help='directory to training and test data', default='data')
    parser.add_argument('-e', '--epochs', help='number of epochs', default=10, type=int)
    parser.add_argument('-b', '--batch', help='batch size', default=32, type=int)
    parser.add_argument('-i', '--image_size', help='image size', default=160, type=int)
    parser.add_argument('-l', '--lr', help='learning rate', default=0.0001, type=float)
    parser.add_argument('-o', '--outputs', help='output directory', default='model')
    parser.add_argument('-f', '--dataset', help='cleaned data listing')
    args = parser.parse_args()

    info('Using TensorFlow v.{}'.format(tf.__version__))
        
    data_path = Path(args.base_path).joinpath(args.data).resolve()
    target_path = Path(args.base_path).resolve().joinpath(args.outputs)
    dataset = data_path.joinpath(args.dataset)
    image_size = args.image_size

    args = {
        "data_path": str(data_path), 
        "image_size": image_size, 
        "epochs": args.epochs, 
        "batch_size": args.batch, 
        "learning_rate": args.lr, 
        "output": str(target_path), 
        "dataset": str(dataset)
    }

    # printing out args for posterity
    for i in args:
        print('{} => {}'.format(i, args[i]))

    run(**args)

    #python train.py -d data/PetImages -e 1 -b 32 -l 0.0001 -o model -f dataset.txt