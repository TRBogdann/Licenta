import tensorflow as tf
from tensorflow.keras.layers import Dropout, BatchNormalization, LeakyReLU, ReLU, Conv2D, MaxPooling2D, UpSampling2D, concatenate, Input
from tensorflow.keras.models import Model

activations = {
    'relu': ReLU,
    'leaky_relu': LeakyReLU
}

def IdentityBlock(x):

    return x

def Normalize(x, normalize):

    return BatchNormalization()(x) if normalize else x

def DropOut(x, drop_out):

    return Dropout(drop_out)(x) if 0.0 < drop_out < 1.0 else x

def EncoderBlock(input_block, filter_size, kernel_size=3, padding="same",
                 activation="relu", slope=0.0, pool_size=(2,2),
                 batch_normalization=False, drop_out=0.0):

    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    pool = MaxPooling2D(pool_size=pool_size)(conv)
    pool = DropOut(pool, drop_out)

    return conv, pool

def BottleneckBlock(input_block, filter_size, kernel_size=3, padding="same",
                    activation="relu", slope=0.0, batch_normalization=False):

    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    return conv

def DecoderBlock(input_block, original_block, filter_size, kernel_size=3, padding="same",
                 activation="relu", slope=0.0, batch_normalization=False, drop_out=0.0):
   
    up = UpSampling2D(size=(2,2))(input_block)
    up = Conv2D(filters=filter_size, kernel_size=kernel_size-1, padding=padding)(up)
    up = Normalize(up, batch_normalization)
    up = activations.get(activation, ReLU)(negative_slope=slope)(up)
    
    merge = concatenate([original_block, up], axis=3)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding)(merge)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    return conv

def OutputBlock(input_block,num_of_classes = 1,kernel_size=1,activation = "sigmoid",padding="same"):
    return Conv2D(filters=num_of_classes,kernel_size=kernel_size,activation=activation,padding=padding)(input_block)


def U_NET(inputs,outputs):
    return Model(inputs,outputs)