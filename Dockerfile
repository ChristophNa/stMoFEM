FROM likask/mofem-spack-jupyterhub

LABEL maintainer="Lukasz.Kaczmarczyk@glasgow.ac.uk"

# Install packages
RUN apt-get update && \
  apt-get install -y \
  build-essential \
  curl \
  software-properties-common \
  git \
  python3 python3-pip \
  sudo && \
  rm -rf /var/lib/apt/lists/*

# RUN useradd mofem \
#   -m -d /mofem_install/jupyter/mofem \
#   -k /mofem_install/jupyter/skel/ \
#   -p paN8aiEIonqJE && \
#   usermod -aG sudo mofem

# Copy spack config
RUN cp -r ~/.spack /mofem_install/spack_config_dir && \ 
  chmod -R aug+rX /mofem_install/spack_config_dir && \
  chmod -R aug+rwX /mofem_install/spack && \
  chown -R mofem:mofem /mofem_install/mofem-cephas && \
  chown -R mofem:mofem /mofem_install/spack && \
  chown -R mofem:mofem /mofem_install/spack_config_dir && \
  chown -R mofem:mofem /mofem_install/core-* && \
  chown -R mofem:mofem /mofem_install/um-*

# Copy static styles for JupyterHub
#RUN mkdir -p /usr/local/share/jupyterhub/static/css && \
#  cp /mofem_install/jupyter/css/* /usr/local/share/jupyterhub/static/css

WORKDIR $MOFEM_INSTALL_DIR

# Define build argument for cache busting
#ARG CACHEBUST=1

RUN git clone https://github.com/ChristophNa/stMoFEM.git app/

RUN pip3 install -r app/requirements.txt


RUN mkdir -p ~/.streamlit/ && echo "[general]"  > ~/.streamlit/credentials.toml && echo "email = \"\""  >> ~/.streamlit/credentials.toml

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Copy the shell script into the container
# COPY start.sh app/start.sh


# # Make the shell script executable
# RUN chmod +x app/tests/start.sh

# # Run the shell script
# ENTRYPOINT ["app/tests/start.sh"]

# Make the shell script executable
RUN chmod +x app/start.sh

# Run the shell script
ENTRYPOINT ["app/start.sh"]
