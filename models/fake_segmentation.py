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

model_path = "./dataOUT/res_tumor_classifier.keras"



tf.config.run_functions_eagerly(True)
model = keras.models.load_model(model_path)
model.summary()

# def stdmat(matrix):
#     return ((matrix - np.mean(matrix)) / np.std(matrix))


def get_img_array(img_path, size, color_mode='rgb'):
    img = keras.utils.load_img(img_path, target_size=size, color_mode=color_mode)
    array = keras.utils.img_to_array(img)
    array = array / 255.0 
    array = np.expand_dims(array, axis=0)
    return array

# img_path = "./dataIN/brain_tumor_classifier/Testing/glioma/Te-gl_0022.jpg"
# img_array = get_img_array(img_path, size=(512,512), color_mode='grayscale')
# cpy = img_array.copy()
# plt.imshow(img_array[0, :, :, :], cmap='gray')
# plt.show()
# res = model.predict(img_array)

# img_tensor = tf.convert_to_tensor(img_array)

# layer_outputs = [layer.output for layer in model.layers if 'conv' in layer.name]
# activation_model = Model(inputs=model.inputs, outputs=layer_outputs)


# activations = activation_model.predict(img_tensor)  

# first_layer_activation = activations[0]  
# num_filters = first_layer_activation.shape[-1]

# for i in range(num_filters):
#     # plt.subplot((num_filters//4+min(num_filters%4,1)), 4, i+1)
#     plt.imshow(stdmat(first_layer_activation[0, :, :, i]), cmap='viridis')
#     # plt.axis('off')
#     plt.show()
# # plt.suptitle("First Conv Layer Activations")



# #2

import os
import random



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

# # Example usage:
base_dir = "./dataIN/brain_tumor_classifier/Testing"
subfolders = ['glioma', 'meningioma', 'notumor', 'pituitary']
n_per_folder = 2  # Or any number you want

random_image_paths = get_random_images_from_folders(base_dir, subfolders, n_per_folder)

def stdmat(matrix):
    return ((matrix - np.mean(matrix)) / np.std(matrix))

def normalise(matrix):
    matrix = np.abs(((matrix - np.mean(matrix)) / np.std(matrix)))
    matrix[matrix < 0] = 0
    matrix  = (matrix - matrix.min()) / (matrix.max() - matrix.min())
    # matrix[matrix > 0.5] += (1 - matrix[matrix > 0.5]/1.5)
    return matrix

plt.figure(figsize=(12, n_per_folder * 4))  # Adjust to control image size

place = 1


for classname in subfolders:
    for img_path  in random_image_paths[classname]:
        img_array = get_img_array(img_path, size=(512,512), color_mode="grayscale")
        cpy = img_array.copy()

        res = model.predict(img_array)

        img_tensor = tf.convert_to_tensor(img_array)

        layer_outputs = [layer.output for layer in model.layers if 'conv' in layer.name]
        activation_model = Model(inputs=model.inputs, outputs=layer_outputs)


        activations = activation_model.predict(img_tensor)  

        first_layer_activation = activations[0]  
        num_filters = first_layer_activation.shape[-1]
        chosen = [random.randrange(0,num_filters,1) for x in range(3)]
        
        plt.subplot(1, 4, 1)
        plt.title(f"{classname}")
        plt.imshow(cpy[0, :, :, :],cmap="gray")
        
        plt.subplot(1, 4, 2)
        plt.title("Activation 1")
        plt.imshow(stdmat(first_layer_activation[0, :, :, chosen[0]]))


        plt.subplot(1, 4, 3)
        plt.title("Activation 2")
        plt.imshow(stdmat(first_layer_activation[0, :, :, chosen[1]]))

        
        plt.subplot(1, 4, 4)
        plt.title("Activation 3")
        plt.imshow(stdmat(first_layer_activation[0, :, :, chosen[2]]))

        plt.show()
        
        plt.subplot(1, 4, 1)
        plt.title(f"{classname}")
        plt.imshow(cpy[0, :, :, :],cmap="gray")
        
        plt.subplot(1, 4, 2)
        plt.title("Correction A1")
        plt.imshow(normalise(first_layer_activation[0, :, :, chosen[0]]))


        plt.subplot(1, 4, 3)
        plt.title("Correction A2")
        plt.imshow(normalise(first_layer_activation[0, :, :, chosen[1]]))

        
        plt.subplot(1, 4, 4)
        plt.title("Correction A3")
        plt.imshow(normalise(first_layer_activation[0, :, :, chosen[2]]))

        plt.show()


