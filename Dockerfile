# Use a base image that's compatible with buildozer's requirements
FROM ubuntu:22.04

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Update apt and install essential packages for buildozer
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-venv \
    openjdk-17-jdk \
    unzip \
    zlib1g-dev \
    libncurses5 \
    libncursesw5 \
    libsdl2-dev \
    libffi-dev \
    pkg-config \
    libc6-dev-i386 \
    apt-utils \
    autoconf \
    automake \
    libtool \
    # *** ADD THE 'zip' COMMAND ***
    zip \
    # *****************************
    && rm -rf /var/lib/apt/lists/*

# Install pip if not already installed or upgrade it
RUN python3 -m ensurepip --default-pip || true
RUN pip install --upgrade pip

# Install Cython (adjust version as per your Kivy version)
RUN pip install "Cython==0.29.33" # Or "Cython==3.0.10" if using Kivy 2.2.0+

# Install buildozer itself using pip
RUN pip install buildozer

# Set a working directory inside the container
WORKDIR /app

ENTRYPOINT ["buildozer"]
