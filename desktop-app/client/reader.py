import os
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from PIL import Image
from skimage import measure


def save_rmn_slices_as_png(logcallback,nifti_path, output_dir, axis=2, mask=False, normalize=True):
    volume = nib.load(nifti_path).get_fdata()
    shape = volume.shape
    max_dim = max(shape)
    
    pad_widths = []
    for dim_size in shape:
        total_pad = max_dim - dim_size
        pad_before = total_pad // 2
        pad_after = total_pad - pad_before
        pad_widths.append((pad_before, pad_after))
    
    volume = np.pad(volume, pad_widths, mode='constant', constant_values=0)
    logcallback(f"[*] Volume shape after transform: {volume.shape}")

    os.makedirs(output_dir, exist_ok=True)

    if normalize:
        volume = volume - np.min(volume)
        if np.max(volume) != 0:
            volume = (volume / np.max(volume)) * 255
        volume = volume.astype(np.uint8)
        
    num_slices = volume.shape[axis]
    
    with open(os.environ['HOME']+"/mri-res/slicer.config", "w") as f:
        f.write(str(num_slices))
        
    logcallback(f"[*] Saving {num_slices} color-coded slices along axis {axis}...")

    for i in range(num_slices):
        if axis == 0:
            slice_2d = volume[i, :, :]
        elif axis == 1:
            slice_2d = volume[:, i, :]
        else:
            slice_2d = volume[:, :, i]
        
        rgba = np.zeros((slice_2d.shape[0], slice_2d.shape[1], 4), dtype=np.uint8)

        if mask:       
            mask_red = (slice_2d > 51) & (slice_2d <= 102)
            mask_green = (slice_2d > 102) & (slice_2d <= 153)
            mask_blue = (slice_2d > 153) & (slice_2d <= 255)

            rgba[mask_red] = [255, 0, 0, 255]    
            rgba[mask_green] = [0, 255, 0, 255]   
            rgba[mask_blue] = [0, 0, 255, 255]

            mask_alpha = (slice_2d > 51)
            rgba[~mask_alpha, 3] = 0  #

        else:
            for x in range(slice_2d.shape[0]):
                for y in range(slice_2d.shape[1]):
                    col = slice_2d[x, y]
                    alpha = 255 if col > 0 else 0
                    rgba[x, y] = [col, col, col, alpha]

        im = Image.fromarray(rgba, mode="RGBA")
        im.save(os.path.join(output_dir, f"slice_{i:03d}.png"))
    logcallback("[*] Done!")


        
    

def create3DModel(
    logcallback, inputPath, outputPath, surface_level=0.5, normalize_color=True
):
    colormap = cm.get_cmap("gray")
    logcallback("[*] Loading NIfTI file...")
    img = nib.load(inputPath)
    volume = img.get_fdata()
    volume = np.nan_to_num(volume)

    shape = volume.shape
    max_dim = max(shape)
    pad_widths = []

    for dim_size in shape:
        total_pad = max_dim - dim_size
        pad_before = total_pad // 2
        pad_after = total_pad - pad_before
        pad_widths.append((pad_before, pad_after))

    volume = np.pad(volume, pad_widths, mode="constant", constant_values=0)
    logcallback(f"[*] Volume shape after padding: {volume.shape}")

    logcallback("[*] Extracting a mesh with marching cubes...")
    verts, faces, normals, values = measure.marching_cubes(
        volume, level=surface_level
    )
    logcallback(f"[*] Extracted {len(verts)} vertices and {len(faces)} faces.")

    vol_shape = volume.shape  # (Z, Y, X)
    min_vals = np.array([0, 0, 0])
    max_vals = np.array([vol_shape[0] - 1, vol_shape[1] - 1, vol_shape[2] - 1])
    scale = max_vals - min_vals
    scale[scale == 0] = 1.0

    def normalize(v):
        # Flip from (Z, Y, X) -> (X, Y, Z) for OpenGl format
        v = v[[2, 1, 0]]
        min_vals_xyz = min_vals[[2, 1, 0]]
        scale_xyz = scale[[2, 1, 0]]
        return ((v - min_vals_xyz) / scale_xyz) * 2.0 - 1.0

    logcallback("[*] Generating triangle array...")
    cpp_data = []

    for face in faces:
        for idx in face:
            v = verts[idx]
            x, y, z = normalize(v)

            if normalize_color and isinstance(values, np.ndarray):
                intensity = values[idx]
                norm_intensity = (intensity - np.min(values)) / (
                    np.max(values) - np.min(values) + 1e-8
                )
                r, g, b, a = colormap(norm_intensity)
            else:
                r = g = b = 0.7
                a = 1.0

            cpp_data += [x, y, z, r, g, b, a]

    logcallback(f"[*] Writing to obj file: {outputPath}")
    with open(outputPath, "w") as f:
        f.write(f"{len(cpp_data)},\n")
        for i in range(0, len(cpp_data), 7):
            for j in range(0, 7):
                if j != 0:
                    f.write(",")
                num = format(cpp_data[i + j], ".6f")
                f.write(f"{num}")

            if i + 7 < len(cpp_data):
                f.write(",\n")

    logcallback("[*] Done")
