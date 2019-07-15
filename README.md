# Cryo-CARE: Content-Aware Image Restoration for Cryo-Transmission Electron Microscopy Data
Tim-Oliver Buchholz<sup>1</sup>, Mareike Jordan, Gaia Pigino, Florian Jug</br>
<sup>1</sup><code>tibuch@mpi-cbg.de</code>

This is an implementation of the Tomo2Tomo denoising scheme for direct-detector movie acquisitions as presented in [the paper](https://arxiv.org/abs/1810.05420). 

To run the exampmles you can either install the required software dependencies yourself or use the singularity container.

Required Software:
* [MotionCor2 v1.2.6 CUDA-9.2](https://msg.ucsf.edu/software)
* [IMOD v4.10.16 (beta-release)](http://bio3d.colorado.edu/ftp/latestIMOD/)
* [CUDA-9.2 for MotionCor2](https://developer.nvidia.com/cuda-92-download-archive)
* [CUDA-9.0 for Tensorflow](https://developer.nvidia.com/cuda-90-download-archive)
* [Tensorflow 1.12](https://www.tensorflow.org/install) `$ pip install tensorflow-gpu==1.12`
* [csbdeep](https://github.com/csbdeep/csbdeep) `$ pip install csbdeep`
* [mrcfile](https://pypi.org/project/mrcfile/) `$ pip install mrcfile`
* [jupyter](https://pypi.org/project/jupyter/) `$ pip install jupyter`


## Download the Example Data
We would like to thank Mareike Jordan from the [Pigino Lab](https://www.mpi-cbg.de/research-groups/current-groups/gaia-pigino/research-focus/) at [MPI-CBG](https://www.mpi-cbg.de) for the example data.

To run the example notebooks you have to do the following:
1. Clone this repository.
2. Download the [example data](https://cloud.mpi-cbg.de/index.php/s/prTOcYsFfPNa1mG/download) and extract it into the `example/data` directory.

## Cryo-CARE Singularity Container
Singularity allows users to have full control of an environment. In a singularity container we can pack specific packages and dependencies. Allowing the deployment of a single singularity image containing all required software. Such a container can then be run on a host system using its hardware. To run a singularity container Singularity has to be installed:
* [Install on Linux](https://singularity.lbl.gov/install-linux)
* [Install on Mac](https://singularity.lbl.gov/install-mac)
* [Install on Windows](https://singularity.lbl.gov/install-windows)

__Note__: The singularity image provided here based on the tensorflow-gpu==1.12 docker image. This docker image comes with CUDA-9.0, which requires a NVIDIA GPU with driver >= 384.81 on the host system. I tested this setup on a Ubuntu 18.04 installation with a NVIDIA GeForce GTX 1050 and driver version 390.116. 

### About the cryo-CARE Singularity Image
This image is built on the tensorflow-gpu==1.12 docker image, which comes with CUDA-9.0. Additionally CUDA-9.2 is installed into the container. We need CUDA-9.2 for `MotionCor2 v1.2.6 CUDA-9.2`. Furthermore all required python dependencies for the cryo-CARE training are installed as well as jupyter.

### Get the Singularity Container
You can either build the singularity image yourself, this requires root access, or you can [download the image](https://cloud.mpi-cbg.de/index.php/s/yqHmKmPnPRQqk5z).

Build instructions:
1. Clone this repository.
2. Change into the directory:</br>
`cd cryoCARE_simg`
3. Build the image:</br>
`sudo singularity build cryoCARE.simg cryoCARE.Singularity`

### Get MotionCor2
Due to licensing we can not ship MotionCor2 directly with the singularity container. You have to download `MotionCor2 v1.2.6 CUDA-9.2` from [here](https://msg.ucsf.edu/software) and place it in the `example` directory. Then we can use it in the example notebooks.

__Note__: It is important to get the CUDA-9.2 version, since we specifically installed CUDA-9.2 in the singularity container.

### Run the Singularity Image
To start a `jupyter notebook` from the singularity image run this command:</br>
`singularity run --nv -B user:/run/user -B example/:/notebooks -B example/data/:/data cryoCARE.simg`

This will display a link to the running jupyter server. Open this link in a browser and you will be able to run the five notebooks:
* `01_Split_Frames.ipynb`: This notebook aligns and splits the movie frames into even/odd halves.
* `02_Tomogram_Reconstruction.ipynb`: This notebook reconstructs the two (even/odd) tomograms based on a previous IMOD-reconstruction.
* `03_Training_Data_Generation.ipynb`: This notebook is used to extract training and validation data.
* `04_Train_cryoCARE_Network.ipynb`: This notebook shows how a cryo-CARE network is trained.
* `05_Predict_cryoCARE.ipynb`: The last notebook is used to apply a trained model to tomographic data.
