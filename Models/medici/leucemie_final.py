import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import keras
import tensorflow as tf
import numpy as np
from keras.src.models import Sequential
from keras.src.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten, Input, LeakyReLU, GlobalAveragePooling2D, BatchNormalization, RandomFlip, RandomRotation, RandomZoom
from keras.src.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.src.regularizers import L2

dir_original_data = "./dataIN/Leucemie/Segmented_Predict"

train_dataset = keras.utils.image_dataset_from_directory(
    dir_original_data,
    labels="inferred",
    label_mode='categorical',
    color_mode='grayscale',
    validation_split=0.2,
    subset='training',
    seed=42,
    image_size=(224, 224)
)

test_dataset = keras.utils.image_dataset_from_directory(
    dir_original_data,
    labels="inferred",
    label_mode='categorical',
    validation_split=0.2,
    color_mode='grayscale',
    subset='validation',
    seed=42,
    image_size=(224, 224)
)


data_augmentation = Sequential([
    RandomFlip("horizontal_and_vertical"),
    RandomRotation(0.2),
])

model = Sequential([
    Input(shape=(224, 224, 1)),
    data_augmentation,
    Conv2D(filters=32, kernel_size=(3, 3), padding='same'),
    BatchNormalization(),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.3),

    Conv2D(filters=64, kernel_size=(3, 3), padding='same'),
    BatchNormalization(),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.3),

    GlobalAveragePooling2D(),
    Dense(64, kernel_regularizer=L2(0.01)),
    BatchNormalization(),
    LeakyReLU(negative_slope=0.01),
    Dropout(0.5),

    Dense(4, activation='softmax', kernel_regularizer=L2(0.01))
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
model_checkpoint = ModelCheckpoint('./dataOUT/leucemie_final.keras', save_best_only=True, monitor='val_loss')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-6)


class_weights_dict = {
    0:1.2,
    1:1.0,
    2:1.0,
    3:1.0
}

history = model.fit(
    train_dataset,
    epochs=20,
    validation_data=test_dataset,
    callbacks=[early_stopping, model_checkpoint, reduce_lr],
    class_weight=class_weights_dict
)