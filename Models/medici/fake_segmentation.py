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

model_path = "./dataOUT/leucemie_final.keras"

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score
import tensorflow as tf
from tensorflow import keras
import cv2

tf.config.run_functions_eagerly(True)
model = keras.models.load_model(model_path)
model.summary()

def get_img_array(img_path, size, color_mode='rgb'):
    img = keras.utils.load_img(img_path, target_size=size, color_mode=color_mode)
    array = keras.utils.img_to_array(img)
    array = array / 255.0 
    array = np.expand_dims(array, axis=0)
    return array

img_path = "./dataIN/Leucemie/Original/Pro/WBC-Malignant-Pro-023.jpg"
img_array = get_img_array(img_path, size=(224,224), color_mode='grayscale')

res = model.predict(img_array)

img_tensor = tf.convert_to_tensor(img_array)

layer_outputs = [layer.output for layer in model.layers if 'conv' in layer.name]
activation_model = Model(inputs=model.inputs, outputs=layer_outputs)


activations = activation_model.predict(img_tensor)  

first_layer_activation = activations[0]  
num_filters = first_layer_activation.shape[-1]

for i in range(min(8, num_filters)):
    plt.subplot(2, 4, i+1)
    plt.imshow(first_layer_activation[0, :, :, i], cmap='viridis')
    plt.axis('off')
plt.suptitle("First Conv Layer Activations")
plt.show()


