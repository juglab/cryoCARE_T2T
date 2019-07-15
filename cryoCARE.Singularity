BootStrap: docker
# This image is built on the tensorflow 1.12 gpu docker image. 
# This image comes with CUDA-9.0 and all required tf dependencies.
From: tensorflow/tensorflow:1.12.0-gpu-py3
	
%post
    apt-get -y update
    pip uninstall -y pip
    apt-get -y install python3-pip
	
	# libtiff5 is needed for MotionCor2
	apt-get -y install libtiff5

	# Install CUDA-9.2 for MotionCor2
    # CUDA 9.2 is not officially supported on ubuntu 18.04 yet, we use the ubuntu 17.10 repository for CUDA instead.
    apt-get update && apt-get install -y --no-install-recommends gnupg2 curl ca-certificates && \
        curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1710/x86_64/7fa2af80.pub | apt-key add - && \
        echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1710/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    	echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list && \
    	apt-get purge --autoremove -y curl && \
    	rm -rf /var/lib/apt/lists/*
    apt-get update && apt-get install -y --no-install-recommends \
        cuda-cudart-9-2=9.2.148-1 \
        && rm -rf /var/lib/apt/lists/*
	apt-get update && apt-get install -y --no-install-recommends \
        cuda-libraries-9-2=9.2.148-1 \
        cuda-nvtx-9-2=9.2.148-1 \
        libnccl2=2.3.7-1+cuda9.2 && \
    	apt-mark hold libnccl2 && \
    	rm -rf /var/lib/apt/lists/*
	apt-get update && apt-get install -y --no-install-recommends \
        cuda-libraries-dev-9-2=9.2.148-1 \
        cuda-nvml-dev-9-2=9.2.148-1 \
        cuda-minimal-build-9-2=9.2.148-1 \
        cuda-command-line-tools-9-2=9.2.148-1 \
        libnccl-dev=2.3.7-1+cuda9.2 && \
    	rm -rf /var/lib/apt/lists/*
    	
    # Install IMOD dependency and wget
    apt-get -y update && apt-get -y install libjpeg62 wget
    
    # Download IMOD
    mkdir /imod
    wget -P /imod http://bio3d.colorado.edu/ftp/latestIMOD/RHEL6-64_CUDA8.0/imod_4.10.16_RHEL6-64_CUDA8.0.sh
    sh /imod/imod_4.10.16_RHEL6-64_CUDA8.0.sh -extract
    ls /
    tar -xzf /IMODtempDir/imod_4.10.16_RHEL6-64_CUDA8.0.tar.gz -C /usr/local
    ln -s /usr/local/imod_4.10.16 /usr/local/IMOD
    cp /usr/local/IMOD/IMOD-linux.* /etc/profile.d
    rm -r /imod
    rm -r /IMODtempDir/imod_4.10.16_RHEL6-64_CUDA8.0.tar.gz

	# Install required Python packages
    pip3 install keras
    pip3 install docopt
    pip3 install tifffile
    pip3 install numpy
    pip3 install csbdeep
    pip3 install mrcfile
    pip3 install jupyter

    apt-get autoremove -y
	apt-get clean

	
	# Remove the example notebooks
	rm -rf /notebooks/*
	
	# Make data directory
	mkdir /data
	
%environment
    . /etc/profile.d/IMOD-linux.sh

%runscript
    echo "Starting notebook..."
    echo "Open browser to localhost:8888"
	exec jupyter notebook --port=8888 --no-browser --ip="0.0.0.0" --notebook-dir='/notebooks'
