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
import cv2


def load_nii_file(filepath):
    nii_file = nib.load(filepath)
    data = np.array(nii_file.get_fdata(), dtype=np.float32)
    data = (data-np.min(data)) / (np.max(data)-np.min(data))
    data = data[50:-50,:,:]
    return data

def load_nii_dataset(input_filepaths, output_filepaths):
    def generator():
        for input_file, output_file in zip(input_filepaths, output_filepaths):
            input_nii = load_nii_file(input_file)
            output_nii = load_nii_file(output_file)
            
            output_nii = np.floor(output_nii*4)
            output_nii = np.where(output_nii>1,1,output_nii)
            
            input_nii = tf.convert_to_tensor(input_nii, dtype=tf.float32)
            output_nii = tf.convert_to_tensor(output_nii, dtype=tf.int32)
            
            input_nii = tf.expand_dims(input_nii, axis=-1)  
            output_nii = tf.expand_dims(output_nii, axis=-1)  
            
            for input_slice,output_slice in zip(input_nii,output_nii):
                yield input_slice,output_slice
    

    dataset = tf.data.Dataset.from_generator(
        generator=generator,
        output_signature=(
            tf.TensorSpec(shape=(240,155,1), dtype=tf.float32),
            tf.TensorSpec(shape=(240,155,1), dtype=tf.float32)
        )
    )
        
    return dataset    

mri_img = load_nii_file('./dataIN/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_flair.nii')
mri_mask = load_nii_file('./dataIN/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_seg.nii')
mri_mask = np.floor(mri_mask*4)
mri_mask = np.where(mri_mask>1,1,mri_mask)

plt.figure(figsize=(10, 10))
plt.subplot(1, 1, 1)
plt.imshow(rotate(montage(mri_img), 90, resize=True), cmap ='gray')

plt.figure(figsize=(10, 10))
plt.subplot(1, 1, 1)
plt.imshow(rotate(montage(mri_mask), 90, resize=True))
plt.show()

input_nii = mri_img
output_nii = mri_mask

input_nii = tf.convert_to_tensor(input_nii, dtype=tf.float32)
output_nii = tf.convert_to_tensor(output_nii, dtype=tf.int32)



input_nii = tf.expand_dims(input_nii, axis=-1)  
output_nii = tf.expand_dims(output_nii, axis=-1)  

print(input_nii.shape)
print(output_nii.shape)