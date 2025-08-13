import os
import keras
import numpy as np
import os
from keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
from PIL import Image

def preprocess_image(image_path, target_size,color_mode="rgb"):
    img = load_img(image_path, color_mode=color_mode)
    img = img.resize(target_size)
    img_array = img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

input_dir = "../dataIN/Leucemie/Original"
output_dir = "../dataIN/Leucemie/Segmented_Predict"
model_path = "../dataOUT/leucemie_seg.keras"

labels = ["Benign","Early","Pre","Pro"]
model = keras.models.load_model(model_path)

for label in labels:
    image_folder = os.path.join(input_dir,label)
    image_files= os.listdir(image_folder)

    for filename in image_files:

        image_path = os.path.join(image_folder,filename)
        
        input_image = preprocess_image(image_path,target_size=(224,224),color_mode='grayscale')
        output_image = model.predict(input_image)[0, :, :, 0]
        
        output_path = os.path.join(output_dir,label)
        output_path = os.path.join(output_path,filename)
        plt.imsave(output_path, output_image, cmap='gray')
        
