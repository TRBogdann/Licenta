import cv2
import numpy as np
from scipy.ndimage import convolve
from PIL import Image
from io import BytesIO
import base64
import tensorflow as tf

def to_numpy(img):
    image = np.asarray(img)
    image = image / 255.
    return image

def leuk_read(pil_image):

    image = np.array(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    kernel_size = 51  
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    background = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    corrected = cv2.subtract(image, background)

    lab = cv2.cvtColor(corrected, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    enhanced = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

    filtered = cv2.medianBlur(enhanced, 3)
    filtered_bgr = cv2.cvtColor(filtered, cv2.COLOR_RGB2BGR)
    
    return to_numpy(filtered_bgr)

def smooth_mask(original,mask):
    
    gray_original = cv2.cvtColor((original*255.0).astype(np.uint8), cv2.COLOR_BGR2GRAY)
 
    mask = (mask*255.0).astype(np.uint8)

    refined = cv2.ximgproc.guidedFilter(
        guide=gray_original,
        src=mask,
        radius=5,
        eps=1e-3,
        dDepth=-1
    )

    refined_mask = refined.astype(np.float32) / 255.0
    return refined_mask

def prepare_for_client(image,mode='RGB',norm=True,resize=(0,0)):
    if mode == 'grayscale':
        image = np.stack([image]*3, axis=-1)
    
    if not norm:
        image = image-np.min(image)
        mx = np.max(image)
        if mx > 0:
            image = image/mx
    
    image = (image*255.).astype(np.uint8)
    image = Image.fromarray(image)

    if resize[0]!=0:
        image = image.resize(resize)
            
    img_bytes = BytesIO()
    image.save(img_bytes,format='PNG')
    img_bytes.seek(0)
    
    return base64.b64encode(img_bytes.read()).decode('utf-8')

def histogram_equalization(image):
    def _equalize(img):
        img = img.astype(np.uint8)
        r, g, b = cv2.split(img)
        r = cv2.equalizeHist(r)
        g = cv2.equalizeHist(g)
        b = cv2.equalizeHist(b)
        return cv2.merge([r, g, b])
        
    equalized = tf.numpy_function(_equalize, [image], tf.uint8)
    equalized.set_shape([256, 256, 3])
    equalized = tf.cast(equalized,tf.float32)
    
    return equalized

def change_range(image):
    return (image - 127.5) / 127.5