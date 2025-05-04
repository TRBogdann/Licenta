
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import keras
import tensorflow as tf
import numpy as np
from keras.src.models import Sequential
from keras.src.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten, Input, LeakyReLU, GlobalAveragePooling2D, BatchNormalization, RandomFlip, RandomRotation
from sklearn.utils.class_weight import compute_class_weight
from keras.src.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.src.regularizers import L2

dir_original_data = "./dataIN/brain_tumor_classifier"

train_dataset = keras.utils.image_dataset_from_directory(
    dir_original_data+"/Training",
    labels="inferred",
    label_mode='categorical',
    color_mode='grayscale',
    seed=42
)

test_dataset = keras.utils.image_dataset_from_directory(
    dir_original_data+"/Testing",
    labels="inferred",
    label_mode='categorical',
    color_mode='grayscale',
    seed=42
)

data_augmentation = Sequential([
    RandomFlip("horizontal"),
    RandomRotation(0.2),
])

model = Sequential([
    Input(shape=(512, 512, 1)),
    data_augmentation,
    Conv2D(filters=32, kernel_size=(3, 3), padding='same'),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.2),

    Conv2D(filters=64, kernel_size=(3, 3), padding='same'),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.2),
    
    Conv2D(filters=128, kernel_size=(3, 3), padding='same'),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.3),
    
    Conv2D(filters=256, kernel_size=(3, 3), padding='same'),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.4),

    GlobalAveragePooling2D(),
    Dense(256, kernel_regularizer=L2(0.01)),
    LeakyReLU(negative_slope=0.01),
    Dropout(0.5),
    

    Dense(4, activation='softmax', kernel_regularizer=L2(0.01))
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

early_stopping = EarlyStopping(monitor='val_loss', patience=13, restore_best_weights=True)
model_checkpoint = ModelCheckpoint('./dataOUT/brain_tumor_classifier.keras', save_best_only=True, monitor='val_loss')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-12)

history = model.fit(
    train_dataset,
    epochs=100,
    validation_data=test_dataset,
    callbacks=[early_stopping, model_checkpoint, reduce_lr]
)