from PIL import Image
import numpy as np
import nibabel as nib
import nilearn as nil
import tempfile

def getClientImage(file,mode='RGB',size=(256,256),to_numpy = False,scale=False,old_size=None):
    image = Image.open(file.stream)
    image = image.convert(mode)
    
    if old_size!=None and len(old_size)>=1:
        old_size[0] = image.size
        
    image = image.resize(size)
    

    if to_numpy:
        image = np.asarray(image)
        if scale:
            image = image / 255.
        
    return image
    

def is_empty(image):
    return np.all(image == 0)

def load_nii_file(filepath,mx = 0):
    nii_file = nib.load(filepath)
    # nii_file = nib.as_closest_canonical(nii_file)
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

    # data = data[:, :, 14:-13]

    return data

def niiFile(file):
    tmp.write(file.stream.read())  # file_stream can be BytesIO or an uploaded file
    tmp.flush()
    