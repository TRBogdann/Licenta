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
import cv2

def overlay(image, mask, cmap=None, alpha=0.4):
    if cmap is None:
        cmap = {
            0: np.array([0, 0, 0]),
            1: np.array([255, 0, 0]), 
            2: np.array([0, 255, 0]),  
            3: np.array([0, 0, 255]),  
        }

    norm_image = cv2.normalize(np.array(image), None, 0, 255, cv2.NORM_MINMAX)
    norm_image = np.uint8(norm_image)
    

    if norm_image.ndim == 2:
        image_rgb = cv2.cvtColor(norm_image, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = norm_image

    mask = np.squeeze(mask, axis=-1) 
    colored_mask = np.zeros_like(image_rgb)
    mask = np.where(mask*4==4 ,3,mask*4) 
    
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            colored_mask[i,j] = cmap[mask[i,j]]
    
    blended_image = cv2.addWeighted(image_rgb, 1 - alpha, colored_mask, alpha, 0)

    return blended_image

def heatmap(image,mask):
    
    norm_image = cv2.normalize(np.array(image), None, 0, 255, cv2.NORM_MINMAX)
    norm_image = np.uint8(norm_image)

    color_dict = {
        0:np.array([0,0,255]),
        2:np.array([0,255,255]),
        3:np.array([0,255,0]),
        1:np.array([255,255,0])
    }

    index_vec = [1,2,0,1]
    growth_vec = [1,-1,-1,1]

    mask = np.squeeze(mask, axis=-1) 
    colored_mask = np.zeros(shape=(norm_image.shape[0],norm_image.shape[1],3))
    mask = np.where(mask*4==4 ,3,mask*4) 
    
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            class_id = mask[i,j]
            index = index_vec[int(class_id)]
            growth = growth_vec[int(class_id)]
            
            color = color_dict[int(class_id)].copy()
            color[index] += growth * norm_image[i,j]
            colored_mask[i,j] = color/255

    
    return colored_mask

input_files = [] 
output_files = []

def load_nii_file(filepath):
    nii_file = nib.load(filepath)
    data = np.array(nii_file.get_fdata(), dtype=np.float32)
    data = (data-np.min(data)) / (np.max(data)-np.min(data))
    data = data[:, :, 14:-13]
    print(data.shape)
    return data

#Vizualizare fisier
nii_file = './dataIN/BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_t2.nii'
data = load_nii_file(nii_file)

nii_file = './dataIN/BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_seg.nii'
mask_data = load_nii_file(nii_file)


input_nii = data
output_nii = mask_data

output_nii = np.where(output_nii == 4, 3, output_nii)

input_nii = tf.convert_to_tensor(input_nii, dtype=tf.float32)
output_nii = tf.convert_to_tensor(output_nii, dtype=tf.float32)

input_nii = tf.expand_dims(input_nii, axis=-1)   
output_nii = tf.expand_dims(output_nii, axis=-1)

print(input_nii.shape)
print(output_nii.shape)

for i in range(50,240):
    input_slice = input_nii[i,:,:]
    mask_slice = output_nii[i,:,:]
    heatmap_slice = heatmap(input_slice,mask_slice)
    overlay_slice = overlay(input_slice,mask_slice)
    
    
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(input_slice,cmap="gray")
    plt.title('Input Image')
    plt.axis('off')

    
    plt.subplot(1, 3, 2)
    plt.imshow(overlay_slice)
    plt.title('Overlay')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.imshow(heatmap_slice)
    plt.title('Heatmap')
    plt.axis('off')

    plt.tight_layout()
    plt.show()
