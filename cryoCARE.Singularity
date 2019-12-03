BootStrap: docker
# This image is built on the tensorflow 1.15 gpu docker image. 
# This image comes with CUDA-9.0 and all required tf dependencies.
From: tensorflow/tensorflow:1.15.0-gpu-py3
	
%post
    apt-get -y update
	
	# libtiff5 is needed for MotionCor2
	apt-get -y install libtiff5
    	
    # Install IMOD dependency and wget
    apt-get -y update && apt-get -y install libjpeg62 wget
    
    # Install CUDA-10.1 for MotionCor2
    apt-get update && apt-get install -y --no-install-recommends gnupg2 curl ca-certificates && \
        curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1810/x86_64/7fa2af80.pub | apt-key add - && \
        echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1810/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    	echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list && \
    	apt-get purge --autoremove -y curl && \
    	rm -rf /var/lib/apt/lists/*
    apt-get update && apt-get install -y --no-install-recommends \
        cuda-cudart-10-1=10.1.168-1 \
        && rm -rf /var/lib/apt/lists/*
	apt-get update && apt-get install -y --no-install-recommends \
        cuda-libraries-10-1=10.1.168-1 \
        cuda-nvtx-10-1=10.1.168-1 \
        libnccl2=2.4.8-1+cuda10.1 && \
    	apt-mark hold libnccl2 && \
    	rm -rf /var/lib/apt/lists/*
	apt-get update && apt-get install -y --no-install-recommends \
        cuda-libraries-dev-10-1=10.1.168-1 \
        cuda-nvml-dev-10-1=10.1.168-1 \
        cuda-minimal-build-10-1=10.1.168-1 \
        cuda-command-line-tools-10-1=10.1.168-1 \
        libnccl-dev=2.4.8-1+cuda10.1 \
        file && \
    	rm -rf /var/lib/apt/lists/*
    
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
    pip install keras==2.2.4
    pip install tifffile==2019.7.26
    pip install csbdeep
    pip install mrcfile
    pip install jupyter

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
