# pull official base image
FROM python:3.11.3

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Debian packages
RUN apt-get update -y \
 && apt-get install -y sudo

RUN adduser --disabled-password --gecos '' docker
RUN adduser docker sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN sudo apt-get install python3-dev -y
RUN sudo apt install tesseract-ocr -y
RUN sudo apt install imagemagick -y
RUN sudo apt install libreoffice -y
RUN sudo apt install default-jre -y
RUN sudo apt install default-jdk -y
RUN sudo apt install abiword -y
RUN sudo apt update
RUN sudo apt-get install build-essential
RUN sudo apt install git -y
RUN sudo apt-get install libicu-dev -y
RUN sudo apt-get install build-essential -y
RUN sudo apt-get install python3-icu -y
RUN sudo apt-get install gunicorn3 -y

# install dependencies
RUN pip install --upgrade pip
RUN pip install scikit-learn
# RUN pip install pdftotree
COPY /etc/appdata/requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

# RUN pip install -r requirements.txt
RUN python -c "import nltk; nltk.download('stopwords')"
RUN python -c "import nltk; nltk.download('wordnet')"
RUN python -c "import nltk; nltk.download('omw-1.4')"
RUN python -c "import nltk; nltk.download('punkt')"
RUN python -c "import nltk; nltk.download('averaged_perceptron_tagger')"
RUN python -c "import nltk; nltk.download('maxent_ne_chunker')"
RUN python -c "import nltk; nltk.download('words')"
RUN python -c "import nltk; nltk.download('stopwords')"



# copy project
COPY . .
