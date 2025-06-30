bash build_all.sh



gdown --folder https://drive.google.com/drive/folders/1DFezOAD0oD1BblsXVxqDsl8fj0qzB82i
gdown --folder https://drive.google.com/drive/folders/1pRyFmxYXmAnpku7nGRioZaKrVJtIsroP
gdown --folder https://drive.google.com/drive/folders/1yMvJmVE07lllLWLys5ASk-_UySep1Dxu

apt update && apt install -y unzip

# Or if you prefer using apt-get
apt-get update && apt-get install -y unzip

cd demo_data
# Extract the kinect driller sequence
unzip kinect_driller_seq.zip

# Extract the mustard archive
unzip mustard0.zip


