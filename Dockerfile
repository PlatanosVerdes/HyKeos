FROM arm32v7/python:3.9-slim

RUN apt-get update && apt-get install -y libjpeg-dev \
        libtiff5-dev \
        libopenjp2-7-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        tk-dev \
        tcl-dev \
        python3-dev

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel
RUN pip install --index-url=https://www.piwheels.org/simple --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./hykeos.py" ]
