import os

path = "/home/x/Downloads/MICCAI_BraTS2020_ValidationData"

def filterFiles(files):
    filtred = []
    for it in files:
        last = it.split('_')[-1]
        if last not in ['flair.nii','seg.nii']:
            filtred.append(it)
    return filtred

for it in os.listdir(path):
    folder = os.path.join(path,it)
    files_to_delete = filterFiles(os.listdir(folder))
    for nii_file in files_to_delete:
        os.remove(os.path.join(folder,nii_file))
    print(f'Removed 3 files from folder:{it}')

