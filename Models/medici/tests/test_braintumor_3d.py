import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import keras
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
from keras.src.saving import register_keras_serializable
import cv2


@register_keras_serializable()
def dice_coefficient(y_true, y_pred, smooth=1e-6):
    y_true_f = tf.reshape(y_true, [-1])  
    y_pred_f = tf.reshape(y_pred, [-1]) 
    
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    union = tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f)

    dice = (2. * intersection + smooth) / (union + smooth)
    return dice

@register_keras_serializable()
def dice_coef_background(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,0] * y_pred[:,:,:,0]))
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,0])) + tf.reduce_sum(tf.square(y_pred[:,:,:,0])) + epsilon)

@register_keras_serializable()
def dice_coef_necrotic(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,1] * y_pred[:,:,:,1]))
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,1])) + tf.reduce_sum(tf.square(y_pred[:,:,:,1])) + epsilon)

@register_keras_serializable()
def dice_coef_edema(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,2] * y_pred[:,:,:,2]))
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,2])) + tf.reduce_sum(tf.square(y_pred[:,:,:,2])) + epsilon)

@register_keras_serializable()
def dice_coef_enhancing(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,3] * y_pred[:,:,:,3]))
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,3])) + tf.reduce_sum(tf.square(y_pred[:,:,:,3])) + epsilon)

@register_keras_serializable()
def multi_class_dice_loss(y_true, y_pred, smooth=1e-6):
    dice_loss_total = 0.0
    #weights = [0.00431145,0.46406451,0.15163813,0.37998591]
    weights = [0.1,1.0,0.4,1.0]
    num_classes = y_pred.shape[-1]

    for class_idx in range(num_classes):
        y_true_class = y_true[..., class_idx]
        y_pred_class = y_pred[..., class_idx]
        
        dice_coef = dice_coefficient(y_true_class, y_pred_class, smooth)
        dice_loss_total += (1 - dice_coef)*weights[class_idx]
        
    return dice_loss_total / num_classes

@register_keras_serializable()
def ajusted_multi_dice(y_true, y_pred, smooth=1e-6):
    dice_loss_total = 0.0
    #weights = [0.00431145,0.46406451,0.15163813,0.37998591]
    weights = [0.1,1.0,0.4,1.0]
    dice_func = [dice_coef_background,dice_coef_necrotic,dice_coef_edema,dice_coef_enhancing]
    num_classes = y_pred.shape[-1]

    for class_idx in range(num_classes):
        dice_coef = dice_func[class_idx](y_true, y_pred, smooth)
        dice_loss_total += (1 - dice_coef)*weights[class_idx]
        
    return dice_loss_total / num_classes

@register_keras_serializable()
def combined_loss(y_true, y_pred):
    dice = ajusted_multi_dice(y_true, y_pred)
    cce = keras.losses.CategoricalCrossentropy()
    return dice + 0.25 * cce(y_true, y_pred)
        
    return dice_loss_total / num_classes

def load_nii_file(filepath,mx = 0):
    nii_file = nib.load(filepath)
    data = np.array(nii_file.get_fdata(), dtype=np.float32)

    if np.all(data==0):
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


def getFile(fileList,fileType):
    for i in fileList:
        if i.find(fileType) != -1:
            return i
    print(fileList)
    raise FileNotFoundError("File not found")

input_path = '../dataIN/BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001'
fileList = os.listdir(input_path)
input_file = [
    getFile(fileList,"_flair."),
    getFile(fileList,"_t1ce."),
    getFile(fileList,"_t1."),
    getFile(fileList,"_t2.")
]

input_file = [os.path.join(input_path, f) for f in input_file]
output_file = os.path.join(input_path,getFile(fileList,"_seg."))

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

input_combined = tf.concat([flair_nii, t1ce_nii, t1_nii, t2_nii], axis=-1)
model_path = '../dataOUT/brats_3d.keras'

input_combined = tf.expand_dims(input_combined, axis=0)

print(input_combined.shape)
model = keras.models.load_model(model_path)

model.summary()
output =model.predict(input_combined)
 

# num_slices = output.shape[0]
# print(output.shape)

# for slice_idx in range(num_slices):
#     plt.figure(figsize=(10, 5))

#     plt.subplot(1, 2, 1)
#     plt.imshow(input_nii[slice_idx, :, :, 0], cmap='gray')
#     plt.title(f'Input Slice {slice_idx}')
#     plt.axis('off')
    
#     segmentation_map = np.argmax(output[slice_idx, :, :], axis=-1)
   
#     plt.subplot(1, 2, 2)
#     plt.imshow(segmentation_map)
#     plt.title(f'Predicted Slice {slice_idx}')
#     plt.axis('off')
    
#     plt.show()