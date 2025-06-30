bash build_all.sh


pip install gdown
apt update && apt install -y unzip

cd demo_data
gdown --folder https://drive.google.com/drive/folders/1DFezOAD0oD1BblsXVxqDsl8fj0qzB82i
gdown --folder https://drive.google.com/drive/folders/1pRyFmxYXmAnpku7nGRioZaKrVJtIsroP

# Extract the kinect driller sequence
unzip kinect_driller_seq.zip

# Extract the mustard archive
unzip mustard0.zip
cd ..
gdown --folder https://drive.google.com/drive/folders/1yMvJmVE07lllLWLys5ASk-_UySep1Dxu

