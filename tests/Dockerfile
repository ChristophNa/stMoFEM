FROM ubuntu:22.04

WORKDIR /tmp

RUN apt-get update && \
  apt-get install -y \
  build-essential \
  curl \
  software-properties-common \
  git \
  python3 python3-pip \
  sudo && \
  rm -rf /var/lib/apt/lists/*

RUN python3 --version

RUN git clone https://github.com/ChristophNa/stMoFEM.git app/

RUN pip3 install -r app/requirements.txt

RUN ls app/

EXPOSE 8501

# Make the shell script executable
RUN chmod +x app/tests/start.sh

# Run the shell script
ENTRYPOINT ["app/tests/start.sh"]
