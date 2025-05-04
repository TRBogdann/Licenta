import tensorflow as tf
import os
from sklearn.model_selection import train_test_split
import numpy as np
import keras
from keras.preprocessing.image import load_img, img_to_array
from PIL import Image
import nibabel as nib

decoder = {
    "png":tf.image.decode_png,
    "jpeg":tf.image.decode_jpeg,
    "image":tf.image.decode_image,
    "bpm":tf.image.decode_bmp,
    "gif":tf.image.decode_gif
}

def preprocess_image(image_path, target_size,color_mode="rgb"):
    img = load_img(image_path, color_mode=color_mode)  
    img = img.resize(target_size)
    img_array = img_to_array(img)
    img_array = img_array / 255.0 
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def apply_gradient(mask,colors):
    height, width = mask.shape
    gradient_image = np.zeros((height, width, 3)) 
    growth = 1/(len(colors)-1)
    for y in range(height):
        for x in range(width):
            value = mask[y, x]
            interval = (int)(value / growth) if value<1 else len(colors)-2

            t = (value - growth * interval) * 2
            gradient_image[y, x] = (1 - t) * colors[interval] + t * colors[interval+1]

    return gradient_image

def load_and_preprocess_image(input_path, output_path, target_size=(256, 256),img_format="png",grayscale=False):

    input_image = tf.io.read_file(input_path)
    output_image = tf.io.read_file(output_path)

    input_image = decoder.get(img_format,"png")(input_image, channels=3)
    output_image = decoder.get(img_format,"png")(output_image, channels=3)

    input_image = tf.image.resize(input_image, target_size)
    output_image = tf.image.resize(output_image, target_size)
    
    if grayscale:
        input_image = tf.image.rgb_to_grayscale(input_image)
        output_image = tf.image.rgb_to_grayscale(output_image)
        
    input_image = tf.cast(input_image, tf.float32) / 255.0
    output_image = tf.cast(output_image, tf.float32) / 255.0

    return input_image, output_image

def create_dataset(input_folder, output_folder,img_format="png", target_size=(256, 256), batch_size=16, test_size=0.2, shuffle=True,grayscale=False):

    input_files = sorted(os.listdir(input_folder))
    output_files = sorted(os.listdir(output_folder))

    assert len(input_files) == len(output_files), "Input and Output folders must have the same number of files."

    input_paths = [os.path.join(input_folder, fname) for fname in input_files]
    output_paths = [os.path.join(output_folder, fname) for fname in output_files]

    train_input_paths, val_input_paths, train_output_paths, val_output_paths = train_test_split(
        input_paths, output_paths, test_size=test_size, random_state=42
    )

    train_dataset = tf.data.Dataset.from_tensor_slices((train_input_paths, train_output_paths))
    val_dataset = tf.data.Dataset.from_tensor_slices((val_input_paths, val_output_paths))
   
    train_dataset = train_dataset.map(
        lambda input_path, output_path: load_and_preprocess_image(input_path, output_path,target_size,img_format=img_format,grayscale=grayscale),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    val_dataset = val_dataset.map(
        lambda input_path, output_path: load_and_preprocess_image(input_path, output_path, target_size,img_format=img_format,grayscale=grayscale),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    if shuffle:
        train_dataset = train_dataset.shuffle(buffer_size=len(train_input_paths))
    train_dataset = train_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    val_dataset = val_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    return train_dataset, val_dataset

def load_nii_file(filepath,first_slice=0,last_slice=-1,extend = False):
    nii_file = nib.load(filepath)
    data = np.array(nii_file.get_fdata(), dtype=np.float32)
    data = data / np.max(data)
    if extend:
        data = np.expand_dims(data, axis=-1)
    
    if first_slice !=0 and last_slice != -1:
        return data[first_slice:last_slice,:,:]
    
    return data

def load_nii_dataset(input_filepaths, output_filepaths, shape=(240, 240, 155),first_slice=0,last_slice=-1,extend = False,encode_depth=1):
    def generator():
        for input_file, output_file in zip(input_filepaths, output_filepaths):
            input_nii = load_nii_file(input_file,first_slice=first_slice,last_slice=last_slice,extend = extend)
            output_nii = load_nii_file(output_file,first_slice=first_slice,last_slice=last_slice,extend = extend and encode_depth==1)
            if encode_depth > 1:
                output_nii = np.floor(output_nii*encode_depth)
                output_nii = tf.convert_to_tensor(output_nii, dtype=tf.int32)
                output_nii = tf.one_hot(output_nii, depth=encode_depth)
            yield input_nii, output_nii
    
    
    output_shape = shape
    input_shape = shape
    
    if extend:
        shape_list = list(shape)
        shape_list.append(1)
        input_shape = tuple(shape_list)
        
        shape_list[-1] = encode_depth
        output_shape = tuple(shape_list)
        
    print(input_shape)
    print(output_shape)
    dataset = tf.data.Dataset.from_generator(
        generator=generator,
        output_signature=(
            tf.TensorSpec(shape=input_shape, dtype=tf.float32),
            tf.TensorSpec(shape=output_shape, dtype=tf.float32)
        )
    )
        
    return dataset

def load_slice_dataset(input_filepaths, output_filepaths, shape=(240, 240, 155),first_slice=0,last_slice=-1,extend = False,encode_depth=1,check=False):
    def generator():
        for input_file, output_file in zip(input_filepaths, output_filepaths):
            input_nii = load_nii_file(input_file,first_slice=first_slice,last_slice=last_slice)
            output_nii = load_nii_file(output_file,first_slice=first_slice,last_slice=last_slice)
            for input_slice,output_slice in zip(input_nii,output_nii):
                if extend:
                    input_slice = np.expand_dims(input_slice, axis=-1)
                    output_slice =  output_slice*encode_depth
                    output_slice = np.where(output_slice==4,3,output_slice)
                    unique_elements, counts = np.unique(output_slice, return_counts=True)
                    output_slice = tf.convert_to_tensor(output_slice, dtype=tf.int32)
                    output_slice = tf.one_hot(output_slice, depth=encode_depth)
                yield input_slice, output_slice
    
    output_shape = shape
    input_shape = shape
    
    if extend:
        shape_list = list(shape)
        shape_list.append(1)
        input_shape = tuple(shape_list)
        
        shape_list[-1] = encode_depth
        output_shape = tuple(shape_list)
        
    print(input_shape)
    print(output_shape)
    dataset = tf.data.Dataset.from_generator(
        generator=generator,
        output_signature=(
            tf.TensorSpec(shape=input_shape, dtype=tf.float32),
            tf.TensorSpec(shape=output_shape, dtype=tf.float32)
        )
    )
        
    return dataset