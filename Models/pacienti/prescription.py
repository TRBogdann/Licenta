import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import numpy as np
import pandas as pd
import tensorflow as tf
from keras.src.layers import StringLookup
from keras.src.models import Sequential
from keras.src.layers import LSTM,Bidirectional,Reshape,Conv2D, MaxPooling2D, Dense, Dropout, Flatten, Input, LeakyReLU, GlobalAveragePooling2D, BatchNormalization,Rescaling, RandomFlip, RandomRotation,RandomBrightness
from sklearn.utils.class_weight import compute_class_weight
from keras.src.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.src.regularizers import L2
from keras.src.models import Model
from utils.callbacks import EvaluateCERCallback

train_dir = "./dataIN/prescriptions/Training/training_words/"
val_dir = "./dataIN/prescriptions/Validation/validation_words/"
df_train = pd.read_csv("./dataIN/prescriptions/Training/training_labels.csv")
df_val = pd.read_csv("./dataIN/prescriptions/Validation/validation_labels.csv")

train_images = df_train['IMAGE'].values
train_labels = df_train['MEDICINE_NAME'].values

val_images = df_val['IMAGE'].values
val_labels = df_val['MEDICINE_NAME'].values

all_text = "".join(train_labels)
vocab = sorted(set(all_text))
vocab = ["[PAD]"] + vocab  
char_to_num = StringLookup(vocabulary=vocab, mask_token=None)
num_to_char = StringLookup(vocabulary=vocab, mask_token=None, invert=True)
num_classes = len(vocab)

print("Vocab size:", num_classes)

def load_and_preprocess_image(filepath, target_size=(256, 128)):
    image = tf.io.read_file(filepath)
    image = tf.image.decode_png(image, channels=1)
    image = tf.image.resize_with_pad(image, target_size[1], target_size[0])
    image = image / 255.0
    return image

def load_dataset(directory, filenames, labels, downsample_factor):
    def map_fn(filename, label):
        filepath = tf.strings.join([directory, filename])
        img = load_and_preprocess_image(filepath)
        
        label_chars = tf.strings.unicode_split(label, input_encoding='UTF-8')
        label_encoded = char_to_num(label_chars)

        label_len = tf.shape(label_encoded)[0]
        input_len = 256 // downsample_factor

        return {
            "image": img,
            "label": label_encoded,
            "input_length": input_len,
            "label_length": label_len
        }

    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
    dataset = dataset.map(map_fn, num_parallel_calls=tf.data.AUTOTUNE)
    return dataset


train_dataset = load_dataset(train_dir, train_images, train_labels,8)
val_dataset = load_dataset(val_dir, val_images, val_labels, 8)

train_dataset = train_dataset.shuffle(buffer_size=df_train.shape[0]).repeat().batch(32).prefetch(tf.data.AUTOTUNE)
val_dataset = val_dataset.batch(32).prefetch(tf.data.AUTOTUNE)

input_img = Input(shape=(128, 256, 1), name="image") 

rnn_shape = (16, 64, 256)

# CNN
x = Conv2D(64, (3, 3), padding="same", activation="relu")(input_img)
x = MaxPooling2D((2, 2))(x)

x = Conv2D(128, (3, 3), padding="same", activation="relu")(x)
x = MaxPooling2D((2, 2))(x)

x = Conv2D(256, (3, 3), padding="same", activation="relu")(x)
x = MaxPooling2D((2, 1))(x)  

x = Reshape((rnn_shape[1], rnn_shape[0] * rnn_shape[2]))(x) 

# RNN
x = Bidirectional(LSTM(128, return_sequences=True))(x)
x = Bidirectional(LSTM(128, return_sequences=True))(x)

#CTC
x = Dense(num_classes, activation="softmax")(x)

model = Model(inputs=input_img, outputs=x)

def ctc_loss(y_true, y_pred):
    return tf.keras.backend.ctc_batch_cost(y_true, y_pred, input_length, label_length)


model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss=ctc_loss,
)


model.summary()

