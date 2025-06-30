bash build_all.sh


pip install gdown
apt update && apt install -y unzip

mkdir demo_data
cd demo_data
gdown --folder https://drive.google.com/drive/folders/1pRyFmxYXmAnpku7nGRioZaKrVJtIsroP # their example data

# Extract the kinect driller sequence
unzip kinect_driller_seq.zip

# Extract the mustard archive
unzip mustard0.zip
cd ..
gdown --folder https://drive.google.com/drive/folders/1yMvJmVE07lllLWLys5ASk-_UySep1Dxu # kobi data
gdown --folder https://drive.google.com/drive/folders/1DFezOAD0oD1BblsXVxqDsl8fj0qzB82i # model weights

mv no_diffusion/ weights