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


@register_keras_serializable()
def dice_coefficient(y_true, y_pred, smooth=1e-6):
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])

    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    union = tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f)

    dice = (2. * intersection + smooth) / (union + smooth)
    return dice

@register_keras_serializable()
def dice_coefficient_loss(y_true, y_pred):
    return 1 - dice_coefficient(y_true, y_pred)

@register_keras_serializable()
def tversky_loss(y_true, y_pred, alpha=0.7, beta=0.3, smooth=1e-6):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    true_pos = tf.reduce_sum(y_true * y_pred)
    false_neg = tf.reduce_sum(y_true * (1 - y_pred))
    false_pos = tf.reduce_sum((1 - y_true) * y_pred)
    return 1 - (true_pos + smooth) / (true_pos + alpha*false_neg + beta*false_pos + smooth)

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
        
model_path = '../dataOUT/brain_part_II.keras'
input_path = '../dataIN/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_flair.nii'
output_path = '../dataIN/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_seg.nii'

input_nii = img.load_nii_file(input_path,first_slice=56,last_slice=-56)
output_nii = img.load_nii_file(output_path,first_slice=56,last_slice=-56)
unmerged_nii = np.where(output_nii > 1, 1, output_nii)
output_nii = np.where(output_nii==4,3,output_nii)


plt.figure(figsize=(10, 10))
plt.subplot(1, 1, 1)
plt.imshow(rotate(montage(input_nii), 90, resize=True), cmap ='gray')
plt.show()

plt.figure(figsize=(10, 10))
plt.subplot(1, 1, 1)
plt.imshow(rotate(montage(output_nii), 90, resize=True))
plt.show()

model = keras.models.load_model(model_path)


for input_slice,unmerged_slice,true_img in zip(input_nii,unmerged_nii,output_nii):
    # Expand dimensions to add the channel dimension
    keep = input_slice
    input_slice = np.expand_dims(input_slice, axis=-1)  
    unmerged_slice = np.expand_dims(unmerged_slice, axis=-1)
    # Add a batch dimension
    input_slice = np.expand_dims(input_slice, axis=0)   
    unmerged_slice = np.expand_dims(unmerged_slice, axis=0)
    # Convert to TensorFlow tensor
    tensor_I = tf.convert_to_tensor(input_slice, dtype=tf.float32)
    tensor_II = tf.convert_to_tensor(unmerged_slice, dtype=tf.float32)
    
    # Predict
    pred = model.predict(tf.concat([tensor_I,tensor_II],axis=3))
    # pred = np.squeeze(pred, axis=0) 
    
 
    pred = model.predict(tensor)
    pred = np.squeeze(pred, axis=0) 
    segmentation_map = np.argmax(pred, axis=-1) 
    
    plt.subplot(1, 3, 1)
    plt.title("Input")
    plt.imshow(rotate(keep, 90, resize=True),cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.title("Predicted")
    plt.imshow(rotate(segmentation_map, 90, resize=True))
    plt.axis('off')


    plt.subplot(1, 3, 3)
    plt.title("True")
    plt.imshow(rotate(true_img, 90, resize=True)) 
    plt.axis('off')
    plt.show()
