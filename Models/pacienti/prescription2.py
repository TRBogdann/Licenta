import sys
import os
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import StringLookup
from keras.models import Model
from keras.layers import Input, Conv2D, MaxPooling2D, Reshape, Bidirectional, LSTM, Dense
from keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load data
train_dir = "./dataIN/prescriptions/Training/training_words/"
val_dir = "./dataIN/prescriptions/Validation/validation_words/"
df_train = pd.read_csv("./dataIN/prescriptions/Training/training_labels.csv")
df_val = pd.read_csv("./dataIN/prescriptions/Validation/validation_labels.csv")

train_images = df_train['IMAGE'].values
train_labels = df_train['MEDICINE_NAME'].values
val_images = df_val['IMAGE'].values
val_labels = df_val['MEDICINE_NAME'].values

# Create vocabulary
all_text = "".join(train_labels)
vocab = sorted(set(all_text))
vocab = ["[PAD]"] + vocab  # Add padding and unknown tokens
char_to_num = StringLookup(vocabulary=vocab, mask_token=None)
num_to_char = StringLookup(vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True)
num_classes = len(char_to_num.get_vocabulary())

arr = [5,21,23,21]
print(num_to_char(arr))

# # Image preprocessing
# def load_and_preprocess_image(filepath, target_size=(256, 128)):
#     image = tf.io.read_file(filepath)
#     image = tf.image.decode_png(image, channels=1)
#     image = tf.image.resize_with_pad(image, target_size[1], target_size[0])
#     image = image / 255.0
#     return image

# # CTC loss function
# def ctc_loss(y_true, y_pred):
#     batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")
#     input_length = tf.cast(tf.shape(y_pred)[1], dtype="int64")
#     label_length = tf.cast(tf.shape(y_true)[1], dtype="int64")
    
#     input_length = input_length * tf.ones(shape=(batch_len, 1), dtype="int64")
#     label_length = label_length * tf.ones(shape=(batch_len, 1), dtype="int64")
    
#     return tf.keras.backend.ctc_batch_cost(y_true, y_pred, input_length, label_length)

# # Data pipeline with padding
# def load_dataset(directory, filenames, labels, downsample_factor, max_label_length=32):
#     def process_sample(filename, label):
#         filepath = tf.strings.join([directory, filename])
#         img = load_and_preprocess_image(filepath)
        
#         # Convert label to tokens
#         label_chars = tf.strings.unicode_split(label, input_encoding='UTF-8')
#         label_encoded = char_to_num(label_chars)
        
#         # Pad label to max length
#         label_encoded = tf.pad(label_encoded, [[0, max_label_length - tf.shape(label_encoded)[0]]])
        
#         return {"image": img}, label_encoded
    
#     dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
#     dataset = dataset.map(process_sample, num_parallel_calls=tf.data.AUTOTUNE)
#     return dataset

# # Model parameters
# downsample_factor = 8
# input_shape = (128, 256, 1)  # height, width, channels
# max_label_length = 32  # Set based on your analysis

# # Create datasets with padding
# train_dataset = load_dataset(train_dir, train_images, train_labels, downsample_factor, max_label_length)
# val_dataset = load_dataset(val_dir, val_images, val_labels, downsample_factor, max_label_length)

# # Batch and prefetch
# train_dataset = train_dataset.shuffle(buffer_size=len(train_images)).batch(32).prefetch(tf.data.AUTOTUNE)
# val_dataset = val_dataset.batch(32).prefetch(tf.data.AUTOTUNE)

# rnn_shape = (16, 64, 256)

# # Model architecture
# input_img = Input(shape=input_shape, name="image")

# # CNN
# x = Conv2D(64, (3, 3), padding="same", activation="relu")(input_img)
# x = MaxPooling2D((2, 2))(x)

# x = Conv2D(128, (3, 3), padding="same", activation="relu")(x)
# x = MaxPooling2D((2, 2))(x)

# x = Conv2D(256, (3, 3), padding="same", activation="relu")(x)
# x = MaxPooling2D((2, 1))(x)  # Only reduce width

# # Prepare for RNN
# x = Reshape((rnn_shape[1], rnn_shape[0] * rnn_shape[2]))(x) 

# # RNN
# x = Bidirectional(LSTM(128, return_sequences=True))(x)
# x = Bidirectional(LSTM(128, return_sequences=True))(x)

# # Output layer
# output = Dense(num_classes+1, activation="softmax")(x)

# # Create model
# model = Model(inputs=input_img, outputs=output)

# # Compile model
# model.compile(
#     optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
#     loss=ctc_loss
# )

# def ctc_decode(y_pred, input_length=64):
#     input_length = input_length * tf.ones(shape=(tf.shape(y_pred)[0],), dtype="int32")
#     decoded = tf.keras.backend.ctc_decode(y_pred, input_length, greedy=True)[0][0]
#     return decoded


# # Callbacks
# early_stopping = EarlyStopping(monitor='val_loss', patience=5, mode='min', verbose=1)
# model_checkpoint = ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True, mode='min')

# # Train
# history = model.fit(
#     train_dataset,
#     validation_data=val_dataset,
#     epochs=100,
#     callbacks=[early_stopping, model_checkpoint],
#     steps_per_epoch=len(train_images) // 32
# )

# # Save model
# model.save('./dataOUT/raw_prescription_model.keras')