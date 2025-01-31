FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV TRANSFORMERLAB_DIR=/opt/transformerlab

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p $CONDA_DIR && \
    rm ~/miniconda.sh

# Create conda environment
RUN conda create -n transformerlab python=3.12 -y
ENV PATH=$CONDA_DIR/envs/transformerlab/bin:$PATH
SHELL ["conda", "run", "-n", "transformerlab", "/bin/bash", "-c"]

# Set working directory
WORKDIR $TRANSFORMERLAB_DIR

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8338

# Command to run the application
CMD ["conda", "run", "--no-capture-output", "-n", "transformerlab", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8338"]
