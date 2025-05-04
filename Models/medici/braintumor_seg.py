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
from utils.unet import U_NET,EncoderBlock3D,DecoderBlock3D,BottleneckBlock3D,OutputBlock3D
from keras.src.callbacks import EarlyStopping,ModelCheckpoint,ReduceLROnPlateau
from keras.src.metrics import Precision,Recall



def load_nii_file(filepath,):
    nii_file = nib.load(filepath)
    data = np.array(nii_file.get_fdata(), dtype=np.float32)
    data = data / np.max(data)
    if extend:
        data = np.expand_dims(data, axis=-1)
    
    if first_slice !=0 and last_slice != -1:
        return data[first_slice:last_slice,:,:]
    
    return data


train_path = './dataIN/MICCAI_BraTS2020_TrainingData'
input_files = [] 
output_files = []


#Vizualizare fisier
mri_img = img.load_nii_file('./dataIN/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_flair.nii')
plt.figure(figsize=(10, 10))
plt.subplot(1, 1, 1)
plt.imshow(rotate(montage(mri_img), 90, resize=True), cmap ='gray')
plt.show()
plt.imshow(rotate(montage(mri_img[50:-50,:,:]), 90, resize=True), cmap ='gray')
plt.show()

img_shape = mri_img[50:-50,:,:].shape

for folder in os.listdir(train_path):
    folder_path = os.path.join(train_path,folder)
    input_file,output_file = os.listdir(folder_path)
    
    if input_file[-5] == 'g':
        input_file,output_file = output_file,input_file
        
    input_files.append(os.path.join(folder_path,input_file))
    output_files.append(os.path.join(folder_path,output_file))
    

X_train,X_validation,y_train,y_validation = train_test_split(input_files,output_files,train_size=0.82)


train_dataset = img.load_nii_dataset(input_filepaths=X_train,
                                     output_filepaths=y_train,
                                     shape=img_shape,
                                     first_slice=50,
                                     last_slice=-50,
                                     extend = True,
                                     encode_depth=4)

val_dataset = img.load_nii_dataset(input_filepaths=X_validation,
                                     output_filepaths=y_validation,
                                     shape=img_shape,
                                     first_slice=50,
                                     last_slice=-50,
                                     extend = True,
                                     encode_depth=4)

train_dataset = train_dataset.batch(16).prefetch(tf.data.experimental.AUTOTUNE)
val_dataset = val_dataset.batch(16).prefetch(tf.data.experimental.AUTOTUNE)

inputs = Input(shape=img_shape+(1,))

conv1,pool1 = EncoderBlock3D(inputs,filter_size=32)
conv2,pool2 = EncoderBlock3D(pool1,filter_size=64)
conv3,pool3 = EncoderBlock3D(pool2,filter_size=128)

neck = BottleneckBlock3D(pool3,filter_size=256)

up1 =  DecoderBlock3D(neck,conv3,filter_size=128)
up2 =  DecoderBlock3D(up1,conv2,filter_size=64)
up3 =  DecoderBlock3D(up2,conv1,filter_size=32)

outputs = OutputBlock3D(up3,num_of_classes=4,kernel_size=(1,1,1),activation='softmax')

model = Model(inputs=inputs,outputs=outputs)
model.summary()

model.compile(
    optimizer='adam',
    loss="categorical_crossentropy"
)

early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
model_checkpoint = ModelCheckpoint('./dataOUT/brain_seg.keras', save_best_only=True, monitor='val_loss')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-6)

history = model.fit(
    train_dataset,
    epochs=10,
    validation_data=val_dataset,
    callbacks=[early_stopping, model_checkpoint, reduce_lr],
)