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
from utils.unet import U_NET,EncoderBlock,DecoderBlock,BottleneckBlock,OutputBlock
from keras.src.callbacks import EarlyStopping,ModelCheckpoint,ReduceLROnPlateau
import keras.src.backend as K
import cv2

distribution = [0,0,0,0]

train_path = './dataIN/BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData'
input_files = [] 
output_files = []

def getFile(fileList,fileType):
    for i in fileList:
        if i.find(fileType) != -1:
            return i
    print(fileList)
    raise FileNotFoundError("File not found")

for folder in os.listdir(train_path):
    try:
     folder_path = os.path.join(train_path,folder)
     fileList = os.listdir(folder_path)
     output_files.append(os.path.join(folder_path,getFile(fileList,"_seg.")))
    except:
        print("Bad Format")
        
def load_nii_file(filepath):
    nii_file = nib.load(filepath)
    data = np.array(nii_file.get_fdata(), dtype=np.float32)
    data = data/4
    data = data[:, :, 14:-13]
    return data

i=0
for it in output_files :
    output_img = load_nii_file(it,)
    output_img = np.floor(output_img*4)
    output_img = np.where(output_img==4,3,output_img)
    
    unique_values,counts = unique_values, counts = np.unique(output_img, return_counts=True)
    
    for val,count in zip(unique_values,counts):
        distribution[int(val)] += count
    
    print(f"File {i} checked")
    i+=1


distribution = np.array(distribution)    
print(distribution/np.sum(distribution))

weights = 1.0 / distribution
weights /= weights.sum()
print(weights)
# print(f"{exceptions} out of {(i-1)*140}")

#24868 final