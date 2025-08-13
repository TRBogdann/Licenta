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
import random

def dice_coefficient(y_true, y_pred, smooth=1e-6):
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])

    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    union = tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f)

    dice = (2. * intersection + smooth) / (union + smooth)
    return dice



def dice_background(y_true, y_pred, smooth=1e-6):
    dice_scores = []

    y_true_class = tf.cast(tf.equal(y_true, 0), tf.float32)
    y_pred_class = tf.cast(tf.equal(y_pred, 0), tf.float32)
        
    intersection = tf.reduce_sum(y_true_class * y_pred_class)
    union = tf.reduce_sum(y_true_class) + tf.reduce_sum(y_pred_class)
  
    dice = (2. * intersection + smooth) / (union + smooth)

    return dice

def dice_c1(y_true, y_pred, smooth=1e-6):
    dice_scores = []

    y_true_class = tf.cast(tf.equal(y_true, 1), tf.float32)
    y_pred_class = tf.cast(tf.equal(y_pred, 1), tf.float32)
        
    intersection = tf.reduce_sum(y_true_class * y_pred_class)
    union = tf.reduce_sum(y_true_class) + tf.reduce_sum(y_pred_class)
  
    dice = (2. * intersection + smooth) / (union + smooth)

    return dice

def dice_c2(y_true, y_pred, smooth=1e-6):
    dice_scores = []

    y_true_class = tf.cast(tf.equal(y_true, 2), tf.float32)
    y_pred_class = tf.cast(tf.equal(y_pred, 2), tf.float32)
        
    intersection = tf.reduce_sum(y_true_class * y_pred_class)
    union = tf.reduce_sum(y_true_class) + tf.reduce_sum(y_pred_class)
  
    dice = (2. * intersection + smooth) / (union + smooth)

    return dice

def dice_c3(y_true, y_pred, smooth=1e-6):
    dice_scores = []

    y_true_class = tf.cast(tf.equal(y_true, 3), tf.float32)
    y_pred_class = tf.cast(tf.equal(y_pred, 3), tf.float32)
        
    intersection = tf.reduce_sum(y_true_class * y_pred_class)
    union = tf.reduce_sum(y_true_class) + tf.reduce_sum(y_pred_class)
  
    dice = (2. * intersection + smooth) / (union + smooth)

    return dice


def augment_image(image, mask):
    if random.random() > 0.5:
        image = tf.image.flip_left_right(image)
        mask = tf.image.flip_left_right(mask)

    if random.random() > 0.5:
        image = tf.image.flip_up_down(image)
        mask = tf.image.flip_up_down(mask)

    k = random.randint(0, 3)
    image = tf.image.rot90(image, k=k)
    mask = tf.image.rot90(mask, k=k)

    return image, mask

def is_empty(image):
    return np.all(image == 0)

def load_nii_file(filepath,mx = 0):
    nii_file = nib.load(filepath)
    data = np.array(nii_file.get_fdata(), dtype=np.float32)
    
    if is_empty(data):
        return data
    
    if mx <= 0:
        data = (data-np.min(data)) / (np.max(data)-np.min(data))
        brain = data > 0  
        mean = data[brain].mean()
        std = data[brain].std()
        data = (data - mean) / std
    else:
        data = data/mx
        
    data = data[:, :, 14:-13]
    
    return data


def load_nii_dataset(input_filepaths, output_filepaths):
    def generator():
        for input_file, output_file in zip(input_filepaths, output_filepaths):
            
            flair_nii = load_nii_file(input_file[0])
            t1ce_nii = load_nii_file(input_file[1])
            t1_nii = load_nii_file(input_file[2])
            t2_nii = load_nii_file(input_file[3])
            
            output_nii = load_nii_file(output_file,mx=4)
            output_nii = np.floor(output_nii*4)
            output_nii = np.where(output_nii == 4, 3, output_nii)

            flair_nii = tf.convert_to_tensor(flair_nii, dtype=tf.float32)
            t1ce_nii = tf.convert_to_tensor(t1ce_nii, dtype=tf.float32)
            t1_nii = tf.convert_to_tensor(t1_nii, dtype=tf.float32)
            t2_nii  = tf.convert_to_tensor(t2_nii , dtype=tf.float32)
            
            output_nii = tf.convert_to_tensor(output_nii, dtype=tf.int32)
            
            flair_nii = tf.expand_dims(flair_nii, axis=-1) 
            t1ce_nii = tf.expand_dims(t1ce_nii, axis=-1)
            t1_nii = tf.expand_dims(t1_nii, axis=-1)
            t2_nii = tf.expand_dims(t2_nii, axis=-1)
              
            output_nii = tf.one_hot(output_nii, depth=4)
            
            
            for i in range(flair_nii.shape[2]):
                img_slice = tf.concat([flair_nii[:,:,i], t1ce_nii[:,:,i], t1_nii[:,:,i], t2_nii[:,:,i]], axis=-1)
                mask_slice = output_nii[:,:,i]
                
                img_slice, mask_slice = augment_image(img_slice, mask_slice)

                yield img_slice, mask_slice
                
    dataset = tf.data.Dataset.from_generator(
        generator=generator,
        output_signature=(
            tf.TensorSpec(shape=(240,240,4), dtype=tf.float32),
            tf.TensorSpec(shape=(240,240,4), dtype=tf.float32)
        )
    )
    
    return dataset


def getFile(fileList,fileType):
    for i in fileList:
        if i.find(fileType) != -1:
            return i
    print(fileList)
    raise FileNotFoundError("File not found")


train_path = './dataIN/BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData'
input_files = [] 
output_files = []


for folder in os.listdir(train_path):
    folder_path = os.path.join(train_path,folder)
    fileList = os.listdir(folder_path)
    
    try:
     input_file = [
         getFile(fileList,"_flair."),
         getFile(fileList,"_t1ce."),
         getFile(fileList,"_t1."),
         getFile(fileList,"_t2.")
     ]
     output_file = getFile(fileList,"_seg.")
        
     input_files.append([os.path.join(folder_path, f) for f in input_file])
     output_files.append(os.path.join(folder_path,output_file))
    except:
        print("Bad file format")
        print(fileList)


j = 1
for input_file, output_file in zip(input_files, output_files):
    
    flair_nii = load_nii_file(input_file[0])
    t1ce_nii = load_nii_file(input_file[1])
    t1_nii = load_nii_file(input_file[2])
    t2_nii = load_nii_file(input_file[3])
    
    output_nii = load_nii_file(output_file,mx=4)
    output_nii = np.floor(output_nii*4)
    output_nii = np.where(output_nii == 4, 3, output_nii)

    flair_nii = tf.convert_to_tensor(flair_nii, dtype=tf.float32)
    t1ce_nii = tf.convert_to_tensor(t1ce_nii, dtype=tf.float32)
    t1_nii = tf.convert_to_tensor(t1_nii, dtype=tf.float32)
    t2_nii  = tf.convert_to_tensor(t2_nii , dtype=tf.float32)
    
    output_nii = tf.convert_to_tensor(output_nii, dtype=tf.int32)
    
    flair_nii = tf.expand_dims(flair_nii, axis=-1) 
    t1ce_nii = tf.expand_dims(t1ce_nii, axis=-1)
    t1_nii = tf.expand_dims(t1_nii, axis=-1)
    t2_nii = tf.expand_dims(t2_nii, axis=-1)
        
    output_nii = tf.one_hot(output_nii, depth=4)
    
    
    for i in range(flair_nii.shape[2]):
        img_slice = tf.concat([flair_nii[:,:,i], t1ce_nii[:,:,i], t1_nii[:,:,i], t2_nii[:,:,i]], axis=-1)
        mask_slice = output_nii[:,:,i]
        
        img_slice, mask_slice = augment_image(img_slice, mask_slice)
        if img_slice.shape != (240, 240, 4):
            raise ValueError(f"Invalid img_slice shape at index {i}: {img_slice.shape}")
        if mask_slice.shape != (240, 240, 4):
            raise ValueError(f"Invalid mask_slice shape at index {i}: {mask_slice.shape}")

    
    print(f"File {j}/{len(output_files)}")
    j+=1


# X_train,X_validation,y_train,y_validation = train_test_split(input_files,output_files,train_size=0.82,random_state=42)

# train_dataset = load_nii_dataset(X_train,y_train)
# val_dataset = load_nii_dataset(X_validation,y_validation)

# train_dataset = train_dataset.batch(16).prefetch(8)

# for input_slice, mask_slice in train_dataset.shuffle(buffer_size=200).take(20):
    
#     input_slice = input_slice[0]
#     mask_slice = mask_slice[0]
#     input_slice = np.mean(input_slice,axis=-1)
#     mask_slice = np.argmax(mask_slice , axis=-1)

#     plt.figure(figsize=(10, 5))

#     plt.subplot(1, 2, 1)
#     plt.imshow(input_slice, cmap='gray')
#     plt.title('Input Image')
#     plt.axis('off')

#     plt.subplot(1, 2, 2)
#     plt.imshow(mask_slice)
#     plt.title('Mask')
#     plt.axis('off')

#     plt.tight_layout()
#     plt.show()

    
# inputs = Input(shape=(240,240,4))

# conv1,pool1 = EncoderBlock(inputs,filter_size=16)
# conv2,pool2 = EncoderBlock(pool1,filter_size=32)

# neck = BottleneckBlock(pool2,filter_size=64)

# up1 =  DecoderBlock(neck,conv2,filter_size=32)
# up2 =  DecoderBlock(up1,conv1,filter_size=16)


# outputs = OutputBlock(up2,num_of_classes=3,activation="softmax")

# model = U_NET(inputs=inputs,outputs=outputs)
# model.summary()
# model.compile(
#     optimizer='adam',
#     loss="categorical_crossentropy",
#     metrics=[dice_coefficient,dice_background,dice_c1,dice_c2,dice_c3]
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