FROM ubuntu:22.04

WORKDIR /tmp

RUN apt-get update && \
  apt-get install -y \
  build-essential \
  curl \
  software-properties-common \
  git \
  python3 python3-pip \
  xvfb \
  libxrender1 \
  sudo && \
  rm -rf /var/lib/apt/lists/* 

RUN export DISPLAY=:99.0 && \
  export PYVISTA_OFF_SCREEN=true && \ 
  Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & 


ARG CACHEBUST=1

# RUN git clone https://github.com/ChristophNa/stMoFEM.git app/

COPY . app/

RUN pip3 install -r app/requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# ENTRYPOINT ["streamlit", "run", "app/tests/app.py", "--server.port=8501", "--server.address=0.0.0.0"]



# Make the shell script executable
RUN chmod +x app/tests/start.sh

# Run the shell script
ENTRYPOINT ["app/tests/start.sh"]
