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
from utils.unet import BottleneckBlock,DecoderBlock,EncoderBlock,OutputBlock,U_NET


def dice_coefficient(y_true, y_pred, smooth=1e-6):
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])

    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    union = tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f)

    dice = (2. * intersection + smooth) / (union + smooth)
    return dice


def dice_coefficient_loss(y_true, y_pred):
    return 1 - dice_coefficient(y_true, y_pred)

def load_nii_file(filepath):
    nii_file = nib.load(filepath)
    data = np.array(nii_file.get_fdata(), dtype=np.float32)
    data = (data - np.min(data)) / (np.max(data) - np.min(data))
    data = data[56:-56, :, :]
    return data

def load_nii_dataset(input_filepaths, output_filepaths):
    def generator():
        for input_file, output_file in zip(input_filepaths, output_filepaths):
            input_nii = load_nii_file(input_file)
            output_nii = load_nii_file(output_file)

            output_nii = np.floor(output_nii * 4)
            
            unmerged_nii = np.where(output_nii > 1, 1, output_nii)
            output_nii = np.where(output_nii > 1, 0, output_nii)

            unmerged_nii = tf.convert_to_tensor(unmerged_nii, dtype=tf.float32)
            input_nii = tf.convert_to_tensor(input_nii, dtype=tf.float32)
            output_nii = tf.convert_to_tensor(output_nii, dtype=tf.float32)

            unmerged_nii = tf.expand_dims(unmerged_nii, axis=-1)
            input_nii = tf.expand_dims(input_nii, axis=-1)
            output_nii = tf.expand_dims(output_nii, axis=-1)

            for i in range(input_nii.shape[0]):
                yield tf.concat([input_nii[i],unmerged_nii[i]],axis=2), output_nii[i]

    dataset = tf.data.Dataset.from_generator(
        generator=generator,
        output_signature=(
            tf.TensorSpec(shape=(240,155,2), dtype=tf.float32),
            tf.TensorSpec(shape=(240,155,1), dtype=tf.float32)
        )
    )

    return dataset

train_path = './dataIN/MICCAI_BraTS2020_TrainingData'
input_files = [] 
output_files = []


for folder in os.listdir(train_path):
     folder_path = os.path.join(train_path,folder)
     input_file,output_file = os.listdir(folder_path)
    
     if input_file[-5] == 'g':
         input_file,output_file = output_file,input_file
        
     input_files.append(os.path.join(folder_path,input_file))
     output_files.append(os.path.join(folder_path,output_file))

X_train,X_validation,y_train,y_validation = train_test_split(input_files,output_files,train_size=0.82,random_state=42)

train_dataset = load_nii_dataset(X_train,y_train)
val_dataset = load_nii_dataset(X_validation,y_validation)

train_dataset = train_dataset.batch(16).prefetch(8)

for input_slice, mask_slice in train_dataset.shuffle(buffer_size=128).take(5):
    # Convert tensors to numpy arrays
    input_slice = input_slice.numpy()
    mask_slice = mask_slice.numpy()
    
    # Since we batched the data, we need to select one example from the batch
    for i in range(input_slice.shape[0]):  # Loop through batch
        current_input = input_slice[i]  # Shape: (240, 155, 2)
        current_mask = mask_slice[i]    # Shape: (240, 155, 1)
        
        plt.figure(figsize=(15, 5))
        
        # Show the first channel (MRI image)
        plt.subplot(1, 3, 1)
        plt.imshow(current_input[:, :, 0], cmap='gray')  # First channel
        plt.title('MRI Input')
        plt.axis('off')
        
        # Show the second channel (unmerged mask)
        plt.subplot(1, 3, 2)
        plt.imshow(current_input[:, :, 1], cmap='gray')  # Second channel
        plt.title('Unmerged Mask')
        plt.axis('off')
        
        # Show the target mask
        plt.subplot(1, 3, 3)
        plt.imshow(current_mask[:, :, 0], cmap='gray')  # Remove last dimension
        plt.title('Target Mask')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
    
# inputs = Input(shape=(240,155,1))

# conv1,pool1 = EncoderBlock(inputs,filter_size=16)
# conv2,pool2 = EncoderBlock(pool1,filter_size=32)

# neck = BottleneckBlock(pool2,filter_size=64)

# up1 =  DecoderBlock(neck,conv2,filter_size=32)
# up2 =  DecoderBlock(up1,conv1,filter_size=16)


# outputs = OutputBlock(up2)

# model = U_NET(inputs=inputs,outputs=outputs)
# model.summary()
# model.compile(
#     optimizer='adam',
#     loss="binary_crossentropy",
#     metrics=[dice_coefficient]
# )

# early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
# model_checkpoint = ModelCheckpoint('/content/brain_part_I.keras', save_best_only=True, monitor='val_loss')
# reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-6)

# history = model.fit(
#     train_dataset,
#     epochs=100,
#     steps_per_epoch=100,
#     validation_data=val_dataset,
#     callbacks=[early_stopping, model_checkpoint, reduce_lr],
# )