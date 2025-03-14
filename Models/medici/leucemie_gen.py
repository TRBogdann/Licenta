import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import keras
import tensorflow as tf
import numpy as np
import pandas as pd
from utils.unet import EncoderBlock,BottleneckBlock,DecoderBlock,OutputBlock,U_NET
import utils.image as img 
from keras import Input
from keras.src.callbacks import EarlyStopping,ModelCheckpoint,ReduceLROnPlateau


#Incarcare Date
dir_input = "./dataIN/Leucemie/Merged/Input"
dir_output = "./dataIN/Leucemie/Merged/Output"

train_dataset,test_dataset = img.create_dataset(dir_input,dir_output,target_size=(224,224),batch_size=8,img_format='jpeg',grayscale=True)

#Contruim modelul UNET

inputs = Input(shape=(224,224,1))

conv1,pool1 = EncoderBlock(inputs,filter_size=32)
conv2,pool2 = EncoderBlock(pool1,filter_size=64)
conv3,pool3 = EncoderBlock(pool2,filter_size=128)

neck = BottleneckBlock(pool3,filter_size=256)

up1 =  DecoderBlock(neck,conv3,filter_size=128)
up2 =  DecoderBlock(up1,conv2,filter_size=64)
up3 =  DecoderBlock(up2,conv1,filter_size=32)

outputs = OutputBlock(up3)

model = U_NET(inputs=inputs,outputs=outputs)

model.compile(
    optimizer='adam',
    loss="binary_crossentropy",
    metrics=['accuracy']
)

early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
model_checkpoint = ModelCheckpoint('./dataOUT/leucemie_seg.keras', save_best_only=True, monitor='val_loss')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-6)

history = model.fit(
    train_dataset,
    epochs=10,
    validation_data=test_dataset,
    callbacks=[early_stopping, model_checkpoint, reduce_lr],
)