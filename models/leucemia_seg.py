import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score
import tensorflow as tf
from tensorflow import keras
import keras
import tensorflow as tf
import numpy as np
from keras.src.models import Sequential
from keras.src.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten, Input, LeakyReLU, GlobalAveragePooling2D, BatchNormalization,Rescaling, RandomFlip, RandomRotation,RandomBrightness
from sklearn.utils.class_weight import compute_class_weight
from keras.src.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.src.regularizers import L2

from keras.layers import RandomRotation
from keras.saving import register_keras_serializable
from tensorflow.keras.models import Model

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score
import tensorflow as tf
from tensorflow import keras
import cv2

model_path = "./dataOUT/leucemie_balanced.keras"



tf.config.run_functions_eagerly(True)
model = keras.models.load_model(model_path)
model.summary()


def get_img_array(img_path, size, color_mode='rgb'):
    img = keras.utils.load_img(img_path, target_size=size, color_mode=color_mode)
    array = keras.utils.img_to_array(img)
    array = array / 255.0 
    array = np.expand_dims(array, axis=0)
    return array

# img_path = "./dataIN/Leucemie/Original/Pro/WBC-Malignant-Pro-023.jpg"
# img_array = get_img_array(img_path, size=(224,224))
# cpy = img_array.copy()

# res = model.predict(img_array)

# img_tensor = tf.convert_to_tensor(img_array)

# layer_outputs = [layer.output for layer in model.layers if 'conv' in layer.name]
# activation_model = Model(inputs=model.inputs, outputs=layer_outputs)


# activations = activation_model.predict(img_tensor)  

# first_layer_activation = activations[0]  
# num_filters = first_layer_activation.shape[-1]

# for i in range(num_filters):
#     plt.subplot((num_filters//4+min(num_filters%4,1)), 4, i+1)
#     plt.imshow(first_layer_activation[0, :, :, i], cmap='viridis')
#     plt.axis('off')
# plt.suptitle("First Conv Layer Activations")
# plt.show()


#2

import os
import random

model_path2 = "./dataOUT/leucemie_seg.keras"
model2 = keras.models.load_model(model_path2)
model2.summary()

def get_random_images_from_folders(base_dir, subfolders, n_per_folder, valid_extensions=('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):

    result = {}

    for sub in subfolders:
        subfolder_path = os.path.join(base_dir, sub)

        if not os.path.exists(subfolder_path):
            print(f"Warning: {subfolder_path} does not exist.")
            result[sub] = []
            continue

        images = [f for f in os.listdir(subfolder_path) if f.lower().endswith(valid_extensions)]

        if len(images) < n_per_folder:
            print(f"Warning: Not enough images in {sub}. Found {len(images)}, required {n_per_folder}. Returning all available.")
            chosen = images  # Return all if fewer than requested
        else:
            chosen = random.sample(images, n_per_folder)

        result[sub] = [os.path.join(subfolder_path, img) for img in chosen]

    return result

# Example usage:
base_dir = "./dataIN/Leucemie/Original"
subfolders = ['Benign', 'Early', 'Pre', 'Pro']
n_per_folder = 2  # Or any number you want

random_image_paths = get_random_images_from_folders(base_dir, subfolders, n_per_folder)

def stdmat(matrix):
    return ((matrix - np.mean(matrix)) / np.std(matrix))

def normalise(matrix):
    matrix = np.abs(((matrix - np.mean(matrix)) / np.std(matrix)))
    matrix[matrix < 0] = 0
    matrix  = (matrix - matrix.min()) / (matrix.max() - matrix.min())
    matrix[matrix > 0.5] += (1 - matrix[matrix > 0.5]/1.5)
    return matrix

place = 1

# total_images = n_per_folder * len(subfolders) * 6  # 6 images per input

# # Calculate rows needed based on 6 columns
# rows = total_images // 6 + (total_images % 6 > 0)

# # Make figure bigger and reduce spacing
# plt.figure(figsize=(18, 3 * rows))  # Adjust size as need

for classname in subfolders:
    for img_path  in random_image_paths[classname]:
        img_array = get_img_array(img_path, size=(224,224))
        cpy = img_array.copy()

        res = model.predict(img_array)

        img_tensor = tf.convert_to_tensor(img_array)

        layer_outputs = [layer.output for layer in model.layers if 'conv' in layer.name]
        activation_model = Model(inputs=model.inputs, outputs=layer_outputs)


        activations = activation_model.predict(img_tensor)  

        first_layer_activation = activations[0]  
        num_filters = first_layer_activation.shape[-1]
        chosen = [random.randrange(0,num_filters,1) for x in range(2)]
        
        img_array_2 = get_img_array(img_path, size=(224,224),color_mode='grayscale')
        predictions = model2.predict(img_array_2) 
        binary_mask = predictions[0, :, :, 0] 
        
        plt.subplot(n_per_folder*4, 6, place)
        plt.title(f"{classname}")
        plt.imshow(cpy[0, :, :, :])
        plt.axis('off')
        place+=1


        plt.subplot(n_per_folder*4, 6, place)
        plt.title("Binary Mask")
        plt.imshow(binary_mask) 
        plt.axis('off')
        place+=1
        
        plt.subplot(n_per_folder*4, 6, place)
        plt.title("CActivation 1")
        plt.imshow(normalise(first_layer_activation[0, :, :, chosen[0]]))
        plt.axis('off')
        place+=1

        plt.subplot(n_per_folder*4, 6, place)
        plt.title("CActivation 2")
        plt.imshow(normalise(first_layer_activation[0, :, :, chosen[1]]))
        plt.axis('off')
        place+=1
        
        plt.subplot(n_per_folder*4, 6, place)
        plt.title("RActivation 1")
        plt.imshow(stdmat(first_layer_activation[0, :, :, chosen[0]]))
        plt.axis('off')
        place+=1

        plt.subplot(n_per_folder*4, 6, place)
        plt.title("RActivation 2")
        plt.imshow(stdmat(first_layer_activation[0, :, :, chosen[1]]))
        plt.axis('off')
        place+=1
        
plt.show()

# model_path2 = "./dataOUT/leucemie_seg.keras"
# model2 = keras.models.load_model(model_path2)
# model2.summary()
# img_array_2 = get_img_array(img_path, size=(224,224),color_mode='grayscale')

# predictions = model2.predict(img_array_2)


# binary_mask = predictions[0, :, :, 0] 


# plt.figure(figsize=(15, 5))


# plt.subplot(1, 2, 1)
# plt.title("Input Image")
# plt.imshow(cpy[0, :, :, :])
# plt.axis('off')


# plt.subplot(1, 2, 2)
# plt.title("Binary Mask")
# plt.imshow(binary_mask) 
# plt.axis('off')

# plt.show()