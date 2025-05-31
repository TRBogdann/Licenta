import tensorflow as tf
from keras.src.layers import Add,Multiply,ZeroPadding2D,Dropout,ZeroPadding3D, BatchNormalization, LeakyReLU, ReLU, Conv2D, MaxPooling2D, UpSampling2D,  Conv3D, MaxPooling3D, UpSampling3D,concatenate, Input
from .custom_layers import activations,DropOut,Normalize,IdentityBlock

def SimpleResidualBlock(input_block, filter_size, kernel_size=(3,3), padding="same",
                 activation="relu", slope=0.0, pool_size=(2,2),
                 batch_normalization=False, drop_out=0.0,scale=True,pool=False,kernel_regularizer=None):

    if scale:
      input_block = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(input_block)
      input_block = Normalize(input_block, batch_normalization)

    conv = Conv2D(filters=filter_size,kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)

    conv = Conv2D(filters=filter_size, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = Add()([conv, input_block])
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)

    if pool:
      conv = MaxPooling2D(pool_size=pool_size)(conv)

    conv = DropOut(conv, drop_out)



    return conv

def ResidualBlock(input_block, filter_size,filter_size_end, kernel_size=(1,1),kernel_size_center=(3,3),scale = False,pool=False, padding="same",
                 activation="relu", slope=0.0, pool_size=(2,2),
                 batch_normalization=False, drop_out=0.0,kernel_regularizer=None):

    if scale:
      input_block = Conv2D(filters=filter_size_end, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(input_block)
      input_block = Normalize(input_block, batch_normalization)

    conv = Conv2D(filters=filter_size,kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)

    conv = Conv2D(filters=filter_size, kernel_size=kernel_size_center, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)

    conv = Conv2D(filters=filter_size_end, kernel_size=kernel_size, padding=padding,kernel_regularizer=kernel_regularizer)(conv)
    conv = Normalize(conv, batch_normalization)
    conv = Add()([conv, input_block])
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)



    if pool:
      conv = MaxPooling2D(pool_size=pool_size)(conv)

    conv = DropOut(conv, drop_out)



    return conv

def StartBlock(input_block, filter_size, kernel_size=(7,7), padding="same",
                 activation="relu", slope=0.0, pool_size=(2,2),strides=2,
                 batch_normalization=False, drop_out=0,kernel_regularizer=None):

    conv = Conv2D(filters=filter_size,kernel_size=kernel_size, padding=padding,strides = strides,kernel_regularizer=kernel_regularizer)(input_block)
    conv = Normalize(conv, batch_normalization)
    conv = activations.get(activation, ReLU)(negative_slope=slope)(conv)
    pool = MaxPooling2D(pool_size=pool_size)(conv)
    pool = DropOut(pool, drop_out)

    return pool

def FlattenResidualBlock(input_block,drop_out=0.0):
    pool = GlobalAveragePooling2D()(input_block)
    pool = DropOut(pool, drop_out)

    return pool