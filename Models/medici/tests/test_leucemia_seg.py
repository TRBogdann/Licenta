import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import keras
import numpy as np
from keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
from PIL import Image
import utils.image as img


color_0 = np.array([0, 0, 0])          
color_1 = np.array([249,220,178])  
color_05 = np.array([190,58,142])       

color_0 = color_0 / 255.0
color_05 = color_05 / 255.0
color_1 = color_1 / 255.0

colors = [
    color_0,         
    color_05,  
    color_1      
]


input_data = "../dataIN/Leucemie/Merged/Input"
output_data = "../dataIN/Leucemie/Merged/Output"
model_path = "../dataOUT/leucemie_seg.keras"

model = keras.models.load_model(model_path)


target_size = (224, 224)  

all_files = os.listdir(input_data)
selected = np.random.randint(0,len(all_files),size=(10))
selected_files = [all_files[i] for i in selected]

for image_file in selected_files:
    image_path = os.path.join(input_data, image_file)  
    output_path = os.path.join(output_data, image_file)
    input_image = img.preprocess_image(image_path, target_size,color_mode='grayscale')
    output_image = img.preprocess_image(output_path,target_size)

    predictions = model.predict(input_image)


    binary_mask = predictions[0, :, :, 0] 


    gradient_mask = img.apply_gradient(binary_mask,colors)

    plt.figure(figsize=(15, 5))


    plt.subplot(1, 4, 1)
    plt.title("Input Image")
    plt.imshow(input_image[0, :, :, 0], cmap='gray')  # Assuming grayscale input
    plt.axis('off')


    plt.subplot(1, 4, 2)
    plt.title("Binary Mask")
    plt.imshow(binary_mask, cmap='gray') 
    plt.axis('off')


    plt.subplot(1, 4, 3)
    plt.title("Gradient Mask")
    plt.imshow(gradient_mask)
    plt.axis('off')

    plt.subplot(1, 4, 4)
    plt.title("Original Mask")
    plt.imshow(output_image[0, :, :, :])
    plt.axis('off')

    plt.show()