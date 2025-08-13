import pandas as pd
import numpy as np
from nn import MLP
from dataset import Dataset
import matplotlib.pyplot as plt

train = Dataset('train',10)
test = Dataset('test',10)
model = MLP(784,10,[256,128,64])
model.fit(train,test,50)

layer0 = model.layers[0].forwardpass(test.x[0])
for i, (img, fmap) in enumerate(zip(test.x[0], layer0)):
    img = img.reshape(28, 28)
    fmap = (fmap - fmap.min()) / (fmap.max() - fmap.min())
    fmap = fmap.reshape(16, 16)
    
    
    plt.figure(figsize=(8, 4))
    
    plt.subplot(1, 2, 1)
    plt.title(f'Image {i}')
    plt.imshow(img, cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title(f'Feature Map {i}')
    plt.imshow(fmap, cmap='viridis')  
    plt.axis('off')
    
    plt.show()