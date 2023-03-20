#!/bin/bash

sudo apt-get -y update
sudo apt-get -y upgrade

sudo apt-get -y install build-essential cmake git unzip pkg-config wget libglu1

mkdir zdownload
cd zdownload
sudo wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
sudo bash Anaconda3-5.0.1-Linux-x86_64.sh

sudo chown -R ubuntu /home/ubuntu/anaconda3
sudo chmod -R +x /home/ubuntu/anaconda3

source ~/.bashrc

conda update -y --all

# start work envrionment
screen -S sample1

mkdir ~/work_dir
cd ~/work_dir

conda create --name keras-tensorflow36 python=3.6

source activate keras-tensorflow36

conda install -y scipy numpy matplotlib scikit-learn pandas

pip install tensorflow
pip install keras

git clone https://iscodesnippet@bitbucket.org/iscodesnippet/keras_multivariate_time_series_forcast_sample1.git

cd keras_multivariate_time_series_forcast_sample1
python run_lstm_model.py

#sudo apt-get -y install python-tk python3-tk
#sudo apt-get -y install python2.7-dev python3-dev