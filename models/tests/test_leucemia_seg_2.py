import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import keras
import numpy as np
from keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
from PIL import Image
import utils.image as img
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


input_data = "../dataIN/Leucemie/Merged/Input"
output_data = "../dataIN/Leucemie/Merged/Output"
model_path = "../dataOUT/leucemie_seg.keras"

# Assuming this loads your model and prepares images as before
model = keras.models.load_model(model_path)
target_size = (224, 224)  

all_files = os.listdir(input_data)
selected = np.random.randint(0,len(all_files),size=len(all_files)//5)
selected_files = [all_files[i] for i in selected]


# Store metrics
accuracies, precisions, recalls, f1s = [], [], [], []

for image_file in selected_files:
    image_path = os.path.join(input_data, image_file)  
    output_path = os.path.join(output_data, image_file)

    input_image = img.preprocess_image(image_path, target_size, color_mode='grayscale')
    output_image = img.preprocess_image(output_path, target_size)

    # Convert mask to grayscale if needed
    if output_image.ndim == 4 and output_image.shape[-1] == 3:
        output_image = np.max(output_image, axis=-1)

# Normalize and binarize
    output_image = (output_image > 0.5).astype(np.uint8)
    prediction = model.predict(input_image)


    pred_mask = (prediction > 0.5).astype(np.uint8)


    y_true = output_image.flatten()
    y_pred = pred_mask.flatten()

    y_true = y_true.squeeze()
    y_pred = y_pred.squeeze()

    # Calculate metrics
    accuracies.append(accuracy_score(y_true, y_pred))
    precisions.append(precision_score(y_true, y_pred, zero_division=0))
    recalls.append(recall_score(y_true, y_pred, zero_division=0))
    f1s.append(f1_score(y_true, y_pred, zero_division=0))

# Print average metrics
print(f"Accuracy: {np.mean(accuracies):.4f}")
print(f"Precision: {np.mean(precisions):.4f}")
print(f"Recall (Sensitivity): {np.mean(recalls):.4f}")
print(f"F1 Score: {np.mean(f1s):.4f}")