FROM python:3.12

RUN apt-get update \
   && apt-get install -y \
     fonts-dejavu \
     ghostscript \
     gnupg2 \
     imagemagick \
     python3-pillow \
     python3-qrcode \
     zbar-tools \
     sed \
   && printf "deb http://http.us.debian.org/debian/ testing non-free contrib main\n" > /etc/apt/sources.list.d/testing.list \
   && apt-get update \
   && apt-get install -y -t testing \
    python3-reedsolo \
   && apt-get autopurge -y \
   && apt-get autoclean -y \
   && sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-6/policy.xml

COPY ./requirements.txt /src/

RUN pip install -r /src/requirements.txt

COPY ./ /src

RUN cd /src \
   && make install

WORKDIR /work

ENTRYPOINT [ "qr-backup" ]
CMD [ "--help" ]
