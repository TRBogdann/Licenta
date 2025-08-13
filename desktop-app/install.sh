cd mri-viewer
mkdir build
cd build
cmake.. && make
cd ../../client
python3 -m venv .venv
pip install -r requirements.txt
sudo mkdir ~/mri-res
sudo cp -r ./model.keras ~/mri-res
sudo cp -r ./mri-analyzer.desktop ~/.local/share/applications
cd ../
chmod +x run.sh