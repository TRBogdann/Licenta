
import keras 
import tensorflow as tf
import pandas as pd
import numpy as np
from keras.src.models import Sequential
from keras.src.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten, Input, LeakyReLU, GlobalAveragePooling2D,BatchNormalization
from sklearn.utils.class_weight import compute_class_weight
from keras.src.callbacks  import EarlyStopping, ModelCheckpoint
from keras.src.regularizers import L1,L2

dir_original_data = "./dataIN/Leucemie/Original"

train_dataset = keras.utils.image_dataset_from_directory(
    dir_original_data,
    labels="inferred",
    label_mode='categorical',
    validation_split= 0.25,
    subset= 'training',
    seed=42
)

test_dataset = keras.utils.image_dataset_from_directory(
    dir_original_data,
    labels="inferred",
    label_mode='categorical',
    validation_split= 0.25,
    subset= 'validation',
    seed=42
)

y_label = []
for images, labels in train_dataset:
    y_label.extend(labels.numpy())  

y_label = np.array(y_label)

y_label_int = []
for it in y_label:
    y_label_int.append(list(it).index(1))
y_label_int = np.array(y_label_int)

class_weights = compute_class_weight("balanced",classes=np.unique(y_label_int),y=y_label_int)

model = Sequential([
    Input(shape=(224, 224, 3)),

    Conv2D(filters=32, kernel_size=(3, 3), padding='same'),
    BatchNormalization(),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(filters=64, kernel_size=(3, 3), padding='same'),
    BatchNormalization(),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.3),

    Conv2D(filters=128, kernel_size=(3, 3), padding='same'),
    BatchNormalization(),
    LeakyReLU(negative_slope=0.01),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.3),

    GlobalAveragePooling2D(),
    Dense(128, kernel_regularizer=L2(0.01)),
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

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

model_checkpoint = ModelCheckpoint(
    './dataOUT/leucemie.keras',
    save_best_only=True,
    monitor='val_loss'
)


history = model.fit(
    train_dataset,
    epochs=12,
    validation_data=test_dataset,
    callbacks=[early_stopping, model_checkpoint],
)

