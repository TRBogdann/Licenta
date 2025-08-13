import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import keras
import tensorflow as tf
import numpy as np
from keras.src.models import Sequential
from keras.src.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten, Input, LeakyReLU, GlobalAveragePooling2D, BatchNormalization, RandomFlip, RandomRotation, RandomZoom
from sklearn.utils.class_weight import compute_class_weight
from keras.src.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.src.regularizers import L2
from utils.loss_functions import focal_loss

dir_original_data = "./dataIN/Leucemie/Original"

train_dataset = keras.utils.image_dataset_from_directory(
    dir_original_data,
    labels="inferred",
    label_mode='categorical',
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
    subset='validation',
    seed=42,
    image_size=(224, 224)
)


y_label = []
for images, labels in train_dataset:
    y_label.extend(labels.numpy())
y_label = np.array(y_label)
y_label_int = np.argmax(y_label, axis=1)
class_weights = compute_class_weight("balanced", classes=np.unique(y_label_int), y=y_label_int)
class_weights_dict = dict(enumerate(class_weights))

data_augmentation = Sequential([
    RandomFlip("horizontal_and_vertical"),
    RandomRotation(0.2),
])

model = Sequential([
    Input(shape=(224, 224, 3)),
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
model_checkpoint = ModelCheckpoint('./dataOUT/leucemie_balanced.keras', save_best_only=True, monitor='val_loss')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-6)

history = model.fit(
    train_dataset,
    epochs=12,
    validation_data=test_dataset,
    callbacks=[early_stopping, model_checkpoint, reduce_lr],
)