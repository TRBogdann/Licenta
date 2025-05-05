
activations = {
    'relu': ReLU,
    'leaky_relu': LeakyReLU,
}

def IdentityBlock(x):

    return x

def Normalize(x, normalize):

    return BatchNormalization()(x) if normalize else x

def DropOut(x, drop_out):

    return Dropout(drop_out)(x) if 0.0 < drop_out < 1.0 else x