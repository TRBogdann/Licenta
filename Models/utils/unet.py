import tensorflow as tf
from keras.src.layers import Add,Multiply,ZeroPadding2D,Dropout,ZeroPadding3D, BatchNormalization, LeakyReLU, ReLU, Conv2D, MaxPooling2D, UpSampling2D,  Conv3D, MaxPooling3D, UpSampling3D,concatenate, Input
from keras.src.models import Model
from custom_layers import activations,DropOut,Normalize,IdentityBlock

def Reshape3D(original_block,up):
    if up.shape[1] != original_block.shape[1] or up.shape[2] != original_block.shape[2] or up.shape[3] != original_block.shape[3]:
        diff_depth = original_block.shape[1] - up.shape[1]
        diff_height = original_block.shape[2] - up.shape[2]
        diff_width = original_block.shape[3] - up.shape[3]

        up = ZeroPadding3D(((diff_depth // 2, diff_depth - diff_depth // 2),
            (diff_height // 2, diff_height - diff_height // 2),
            (diff_width // 2, diff_width - diff_width // 2))
        )(up)
    return up

def Reshape2D(original_block, up):
    if up.shape[1] != original_block.shape[1] or up.shape[2] != original_block.shape[2]:
        diff_height = original_block.shape[1] - up.shape[1]
        diff_width = original_block.shape[2] - up.shape[2]

        up = ZeroPadding2D(((diff_height // 2, diff_height - diff_height // 2),
                            (diff_width // 2, diff_width - diff_width // 2)))(up)
    return up



def EncoderBlock(input_block, filter_size, kernel_size=3, padding="same",
                 activation="relu", slope=0.0, pool_size=(2,2),
                 batch_normalization=False, drop_out=0.0,kernel_regularizer=None):

    conv = Conv2D(filters=filter_size,kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    pool = MaxPooling2D(pool_size=pool_size)(conv)
    pool = DropOut(pool, drop_out)

    return conv, pool

def BottleneckBlock(input_block, filter_size, kernel_size=3, padding="same",
                    activation="relu", slope=0.0, batch_normalization=False,kernel_regularizer=None):

    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    return conv

def DecoderBlock(input_block, original_block, filter_size, kernel_size=3, padding="same",
                 activation="relu", slope=0.0, batch_normalization=False, drop_out=0.0,kernel_regularizer=None):
   
    up = UpSampling2D(size=(2,2))(input_block)
    up = Reshape2D(original_block=original_block,up = up)
    merge = concatenate([original_block, up], axis=3)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(merge)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    return conv

def OutputBlock(input_block,num_of_classes = 1,kernel_size=1,activation = "sigmoid",padding="same",kernel_regularizer=None):
    return Conv2D(filters=num_of_classes,kernel_size=kernel_size,activation=activation,padding=padding,kernel_regularizer=kernel_regularizer)(input_block)



def EncoderBlock3D(input_block, filter_size, kernel_size=3, padding="same",
                 activation="relu", slope=0.0, pool_size=(2, 2, 2),
                 batch_normalization=False, drop_out=0.0,kernel_regularizer=None):
    
    conv = Conv3D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv3D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)

    pool = MaxPooling3D(pool_size=pool_size)(conv)
    pool = DropOut(pool, drop_out)

    return conv, pool

def BottleneckBlock3D(input_block, filter_size, kernel_size=3, padding="same",
                    activation="relu", slope=0.0, batch_normalization=False,kernel_regularizer=None):
    conv = Conv3D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv3D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    return conv

def AttentionDecoder(input_block, original_block, filter_size, kernel_size=3, padding="same",
                    activation="relu", slope=0.0, batch_normalization=False,kernel_regularizer=None):
    
    up = UpSampling2D(size=(2, 2))(input_block)
    up = Reshape2D(original_block=original_block, up=up)
    
    theta_x = Conv2D(filter_size, kernel_size=kernel_size, strides=1, padding=padding)(original_block)
    phi_g = Conv2D(filter_size, kernel_size=kernel_size, strides=1, padding=padding)(up)
    
    attention = Add()([theta_x, phi_g])
    attention = Normalize(attention, batch_normalization)
    attention = activations.get(activation, ReLU)(negative_slope=slope)(attention)
    attention = Conv2D(1, kernel_size=kernel_size, activation='sigmoid', padding=padding,kernel_regularizer=kernel_regularizer)(attention)
    
    attention = Multiply()([original_block, attention])
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(attention)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    return conv


    
def AttentionDecoder3D(input_block, original_block, filter_size, kernel_size=3, padding="same",
                    activation="relu", slope=0.0, batch_normalization=False,kernel_regularizer=None):
    
    up = UpSampling3D(size=(2, 2, 2))(input_block)
    up = Reshape3D(original_block=original_block, up=up)

    theta_x = Conv3D(filter_size, kernel_size=kernel_size, strides=1, padding=padding)(original_block)
    phi_g = Conv3D(filter_size, kernel_size=kernel_size, strides=1, padding=padding)(up)

    attention = Add()([theta_x, phi_g])
    attention = Normalize(attention, batch_normalization)
    attention = activations.get(activation, ReLU)(negative_slope=slope)(attention)
    attention = Conv3D(1, kernel_size=kernel_size, activation='sigmoid', padding=padding,kernel_regularizer=kernel_regularizer)(attention)

    attention = Multiply()([original_block, attention]) 
    
    conv = Conv3D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(attention)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv3D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    return conv


def DecoderBlock3D(input_block, original_block, filter_size, kernel_size=3, padding="same",
                 activation="relu", slope=0.0, batch_normalization=False, drop_out=0.0,kernel_regularizer=None):
    
    up = UpSampling3D(size=(2, 2, 2))(input_block)
    up = Reshape3D(original_block=original_block,up=up)
    merge = concatenate([original_block, up], axis=-1)
    
    conv = Conv3D(filters=filter_size, kernel_size=kernel_size, padding=padding, kernel_regularizer=kernel_regularizer)(merge)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    conv = Conv3D(filters=filter_size, kernel_size=kernel_size, padding=padding, kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    
    return conv

def OutputBlock3D(input_block, num_of_classes=1, kernel_size=1, activation="sigmoid", padding="same",kernel_regularizer=None):
    return Conv3D(filters=num_of_classes, kernel_size=kernel_size, activation=activation, padding=padding, kernel_regularizer=kernel_regularizer)(input_block)

def U_NET(inputs,outputs):
    return Model(inputs,outputs)