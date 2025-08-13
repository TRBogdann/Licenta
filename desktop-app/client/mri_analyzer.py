
import keras
import numpy as np
import tensorflow as tf
import pandas as pd
import nibabel as nib
import nilearn as nil
import scipy.ndimage as ndi
import matplotlib.pyplot as plt
from skimage.util import montage
from skimage.transform import rotate,resize
from keras.src.saving import register_keras_serializable
import cv2
import os
from scipy.ndimage import label, binary_dilation

def remove_outer_layer_3d(mask, threshold=0.4):
    class1 = (mask == 3)
    class3 = (mask == 1)

    labeled, num_features = label(class3)

    se = np.ones((3, 3, 3), dtype=bool)

    for region_id in range(1, num_features + 1):
        region = (labeled == region_id)

        dilated = binary_dilation(region, structure=se)

        border = dilated & (~region)

        class1_ratio = np.sum(class1[border]) / border.sum() if border.sum() > 0 else 0

        if class1_ratio < threshold:
            mask[region] = 2

    return mask


def remove_outer_layer(mask,threshold = 0.75):

    class1 = (mask == 3)
    class3 = (mask == 1)

    labeled, num_features = label(class3)

    se = np.ones((3, 3), dtype=bool)

    for region_id in range(1, num_features + 1):
        region = (labeled == region_id)

        dilated = binary_dilation(region, structure=se)

        border = dilated & (~region)

        class1_ratio = np.sum(class1[border]) / border.sum()

        if class1_ratio < threshold:
            mask[region] = 2


    return mask

def ajust_mask(mask):
    mask = np.squeeze(mask, axis=0)
    mask = np.argmax(mask, axis=-1)

    mask = remove_outer_layer_3d(mask)

    mask = tf.convert_to_tensor(mask, dtype=tf.int32)
    mask = tf.one_hot(mask, depth=4)
    mask = tf.expand_dims(mask, axis=0)

    return mask

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
def dice_coef_background(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,:,0] * y_pred[:,:,:,:,0]), axis=[1, 2, 3])
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,:,0]), axis=[1, 2, 3]) + tf.reduce_sum(tf.square(y_pred[:,:,:,:,0]), axis=[1, 2, 3]) + epsilon)

@register_keras_serializable()
def dice_coef_necrotic(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,:,1] * y_pred[:,:,:,:,1]), axis=[1, 2, 3])
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,:,1]), axis=[1, 2, 3]) + tf.reduce_sum(tf.square(y_pred[:,:,:,:,1]), axis=[1, 2, 3]) + epsilon)

@register_keras_serializable()
def dice_coef_edema(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,:,2] * y_pred[:,:,:,:,2]), axis=[1, 2, 3])
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,:,2]), axis=[1, 2, 3]) + tf.reduce_sum(tf.square(y_pred[:,:,:,:,2]), axis=[1, 2, 3]) + epsilon)

@register_keras_serializable()
def dice_coef_enhancing(y_true, y_pred, epsilon=1e-6):
    intersection = tf.reduce_sum(tf.abs(y_true[:,:,:,:,3] * y_pred[:,:,:,:,3]), axis=[1, 2, 3])
    return (2. * intersection) / (tf.reduce_sum(tf.square(y_true[:,:,:,:,3]), axis=[1, 2, 3]) + tf.reduce_sum(tf.square(y_pred[:,:,:,:,3]), axis=[1, 2, 3]) + epsilon)

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
    weights = [0.04,0.36,0.16,0.44]
    dice_func = [dice_coef_background,dice_coef_necrotic,dice_coef_edema,dice_coef_enhancing]
    num_classes = y_pred.shape[-1]

    for class_idx in range(num_classes):
        dice_coef = dice_func[class_idx](y_true, y_pred, smooth)
        dice_loss_total += (1 - dice_coef)*weights[class_idx]

    return dice_loss_total / num_classes

@register_keras_serializable()
def reverse_containment_penalty(y_pred):

    C1 = y_pred[..., 1]
    C2 = y_pred[..., 2]
    C3 = y_pred[..., 3]

    c2_in_c1 = tf.reduce_mean(C2 * C1)
    c2_in_c3 = tf.reduce_mean(C2 * C3)
    c1_in_c3 = tf.reduce_mean(C1 * C3)

    total_violation = c2_in_c1 + c2_in_c3 + c1_in_c3

    normalized_penalty = total_violation / 3.0
    return normalized_penalty

@register_keras_serializable()
def combined_loss(y_true, y_pred):
    dice = ajusted_multi_dice(y_true, y_pred)
    cce = keras.losses.CategoricalCrossentropy()
    penalty = reverse_containment_penalty(y_pred)
    return 0.65*dice + 0.25*cce(y_true, y_pred) + 0.1*penalty




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

            input_combined = tf.concat([flair_nii, t1ce_nii, t1_nii, t2_nii], axis=-1)

            output_nii = tf.one_hot(output_nii, depth=4)

            yield input_combined, output_nii

    dataset = tf.data.Dataset.from_generator(
        generator=generator,
        output_signature=(
            tf.TensorSpec(shape=(240,240,128,4), dtype=tf.float32),
            tf.TensorSpec(shape=(240,240,128,4), dtype=tf.float32)
        )
    )

    return dataset

def getFile(fileList,fileType):
    for i in fileList:
        if i.find(fileType) != -1:
            return i
    print(fileList)
    raise FileNotFoundError("File not found")

def createMask(logcallback,input_file):
    
    logcallback("[*] Combining slices...")
    
    flair_nii = load_nii_file(input_file[0])
    t1ce_nii = load_nii_file(input_file[1])
    t1_nii = load_nii_file(input_file[2])
    t2_nii = load_nii_file(input_file[3])

    flair_nii = tf.convert_to_tensor(flair_nii, dtype=tf.float32)
    t1ce_nii = tf.convert_to_tensor(t1ce_nii, dtype=tf.float32)
    t1_nii = tf.convert_to_tensor(t1_nii, dtype=tf.float32)
    t2_nii  = tf.convert_to_tensor(t2_nii , dtype=tf.float32)

    flair_nii = tf.expand_dims(flair_nii, axis=-1)
    t1ce_nii = tf.expand_dims(t1ce_nii, axis=-1)
    t1_nii = tf.expand_dims(t1_nii, axis=-1)
    t2_nii = tf.expand_dims(t2_nii, axis=-1)

    input_combined = tf.concat([flair_nii, t1ce_nii, t1_nii, t2_nii], axis=-1)
    model_path = os.environ['HOME']+'/mri-res/model.keras'
    input_combined = tf.expand_dims(input_combined, axis=0)

    logcallback("[*] Loading model...")
    model = keras.models.load_model(model_path)

    logcallback("[*] Analyzing brain scan...")
    output = model.predict(input_combined)
    
    logcallback("[*] Creating masks...")
    output = ajust_mask(output)
    output = np.squeeze(output, axis=0)
    output = np.argmax(output, axis=-1)

    affine = np.eye(4)
    hdr = nib.Nifti1Header()
    hdr.set_data_dtype(np.int64)
    nii_img = nib.Nifti1Image(output, affine,header=hdr)
    nib.save(nii_img, os.environ['HOME']+'/mri-res/segmentation.nii')
    logcallback("[*] Mask saved")