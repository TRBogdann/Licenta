import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import tensorflow as tf
import pandas as pd
import nibabel as nib
import nilearn as nil
import scipy.ndimage as ndi
import matplotlib.pyplot as plt
import utils.image as img
from skimage.util import montage
from skimage.transform import rotate,resize
from sklearn.model_selection import train_test_split
from keras.src import Input
from keras.src.models import Model
from utils.unet import U_NET,AttentionDecoder,EncoderBlock,DecoderBlock,BottleneckBlock,OutputBlock
from keras.src.callbacks import EarlyStopping,ModelCheckpoint,ReduceLROnPlateau
import keras.src.backend as K

def dice_coefficient(y_true, y_pred, smooth=1e-6):
    y_true_f = tf.reshape(y_true, [-1])  
    y_pred_f = tf.reshape(y_pred, [-1]) 
    
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    union = tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f)

    dice = (2. * intersection + smooth) / (union + smooth)
    return dice

def multi_class_dice_loss(y_true, y_pred, smooth=1e-6):
    dice_loss_total = 0.0
    
    num_classes = y_pred.shape[-1]

    for class_idx in range(num_classes):
        y_true_class = y_true[..., class_idx]
        y_pred_class = y_pred[..., class_idx]
        
        dice_coef = dice_coefficient(y_true_class, y_pred_class, smooth)
        dice_loss_total += 1 - dice_coef
        
    return dice_loss_total / num_classes

def dice_coef_necrotic(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,1] * y_pred[:,:,:,1]))
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,1])) + tf.reduce_sum(tf.square(y_pred[:,:,:,1])) + epsilon)

def dice_coef_edema(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,2] * y_pred[:,:,:,2]))
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,2])) + tf.reduce_sum(tf.square(y_pred[:,:,:,2])) + epsilon)

def dice_coef_enhancing(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,3] * y_pred[:,:,:,3]))
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,3])) + tf.reduce_sum(tf.square(y_pred[:,:,:,3])) + epsilon)

train_path = './dataIN/MICCAI_BraTS2020_TrainingData'
input_files = [] 
output_files = []


#Vizualizare fisier
mri_img = img.load_nii_file('./dataIN/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_flair.nii')
mri_mask = img.load_nii_file('./dataIN/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_seg.nii')

plt.figure(figsize=(10, 10))
plt.subplot(1, 1, 1)
plt.imshow(rotate(montage(mri_img), 90, resize=True), cmap ='gray')
plt.show()
plt.imshow(rotate(montage(mri_img[50:-50,:,:]), 90, resize=True), cmap ='gray')
plt.show()

plt.figure(figsize=(10, 10))
plt.subplot(1, 1, 1)
plt.imshow(rotate(montage(mri_mask), 90, resize=True))
plt.show()
plt.imshow(rotate(montage(mri_mask[50:-50,:,:]), 90, resize=True))
plt.show()

frames_per_mri = mri_img.shape[0]-100
img_shape = mri_img[0].shape

for folder in os.listdir(train_path):
    folder_path = os.path.join(train_path,folder)
    input_file,output_file = os.listdir(folder_path)
    
    if input_file[-5] == 'g':
        input_file,output_file = output_file,input_file
        
    input_files.append(os.path.join(folder_path,input_file))
    output_files.append(os.path.join(folder_path,output_file))


X_train,X_validation,y_train,y_validation = train_test_split(input_files,output_files,train_size=0.82)

train_size = frames_per_mri*len(X_train)
print(train_size)

train_dataset = img.load_slice_dataset(input_filepaths=X_train,
                                     output_filepaths=y_train,
                                     shape=img_shape,
                                     first_slice=50,
                                     last_slice=-50,
                                     extend = True,
                                     encode_depth=4)

val_dataset = img.load_slice_dataset(input_filepaths=X_validation,
                                     output_filepaths=y_validation,
                                     shape=img_shape,
                                     first_slice=50,
                                     last_slice=-50,
                                     extend = True,
                                     encode_depth=4)


train_dataset = train_dataset.shuffle(buffer_size=3200)
train_dataset = train_dataset.batch(16).prefetch(tf.data.AUTOTUNE)
val_dataset = val_dataset.batch(16).prefetch(tf.data.AUTOTUNE)

inputs = Input(shape=(240,155,1))

conv1,pool1 = EncoderBlock(inputs,filter_size=32)
conv2,pool2 = EncoderBlock(pool1,filter_size=64)

neck = BottleneckBlock(pool2,filter_size=128)

up1 =  AttentionDecoder(neck,conv2,filter_size=64)
up2 =  AttentionDecoder(up1,conv1,filter_size=32)

outputs = OutputBlock(up2,num_of_classes=4,kernel_size=1,activation='softmax')

model = U_NET(inputs=inputs,outputs=outputs)

model.compile(
    optimizer='adam',
    loss=multi_class_dice_loss,
    metrics=['accuracy']
)

early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
model_checkpoint = ModelCheckpoint('./dataOUT/leucemie_seg.keras', save_best_only=True, monitor='val_loss')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-6)

history = model.fit(
    train_dataset,
    epochs=10,
    validation_data=val_dataset,
    callbacks=[early_stopping, model_checkpoint, reduce_lr],
)
