
def is_empty(image):
    return np.all(image == 0)

def load_nii_file(filepath,mx = 0):
    nii_file = nib.load(filepath)
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
        
    data = data[:, :, 14:-13]
    
    return data


def load_nii_dataset(input_filepaths, output_filepaths):
    def generator():
        for input_file, output_file in zip(input_filepaths, output_filepaths):
            
            flair_nii = load_nii_file(input_file[0])
            t1ce_nii = load_nii_file(input_file[1])
            t1_nii = load_nii_file(input_file[2])
            t2_nii = load_nii_file(input_file[3])
            
            output_nii = load_nii_file(output_file,mx=4)
            output_nii = np.floor(output_nii*4)
            output_nii = np.where(output_nii == 4, 3, output_nii)

            flair_nii = tf.convert_to_tensor(flair_nii, dtype=tf.float32)
            t1ce_nii = tf.convert_to_tensor(t1ce_nii, dtype=tf.float32)
            t1_nii = tf.convert_to_tensor(t1_nii, dtype=tf.float32)
            t2_nii  = tf.convert_to_tensor(t2_nii , dtype=tf.float32)
            
            output_nii = tf.convert_to_tensor(output_nii, dtype=tf.int32)
            
            flair_nii = tf.expand_dims(flair_nii, axis=-1) 
            t1ce_nii = tf.expand_dims(t1ce_nii, axis=-1)
            t1_nii = tf.expand_dims(t1_nii, axis=-1)
            t2_nii = tf.expand_dims(t2_nii, axis=-1)

            input_combined = tf.concat([flair_nii, t1ce_nii, t1_nii, t2_nii], axis=-1)

            output_nii = tf.one_hot(output_nii, depth=4)

            yield input_combined, output_nii
                
    dataset = tf.data.Dataset.from_generator(
        generator=generator,
        output_signature=(
            tf.TensorSpec(shape=(240,240,128,4), dtype=tf.float32),
            tf.TensorSpec(shape=(240,240,128,4), dtype=tf.float32)
        )
    )
    
    return dataset
