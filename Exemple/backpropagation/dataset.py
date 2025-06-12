import os
from PIL import Image
import numpy as np

class Dataset:
    def __init__(self, path, classes, batch_size=32):
        self.batch_size = batch_size
        self.classes = classes
        folders = os.listdir(path)
        unbatched_x = []
        unbatched_y = []
        for folder in folders:
            label = int(folder)
            y = np.zeros(classes)
            y[label] = 1.0

            image_folder_path = os.path.join(path, folder)
            for image_name in os.listdir(image_folder_path):
                image_path = os.path.join(image_folder_path, image_name)
                x = np.array(Image.open(image_path).convert('L'))
                x = x.astype(np.float32) / 255.0
                x = x.flatten()
                unbatched_x.append(x)
                unbatched_y.append(y.copy())

        missing = len(unbatched_x) % batch_size
        if missing != 0:
            indexes = np.random.randint(0, len(unbatched_x), batch_size - missing)
            for index in indexes:
                unbatched_x.append(unbatched_x[index].copy())
                unbatched_y.append(unbatched_y[index].copy())

        indices = np.random.permutation(len(unbatched_x))
        unbatched_x = np.array(unbatched_x)[indices]
        unbatched_y = np.array(unbatched_y)[indices]

        self.x = unbatched_x.reshape(-1, batch_size, unbatched_x.shape[-1])
        self.y = unbatched_y.reshape(-1, batch_size, unbatched_y.shape[-1])
