FROM phusion/baseimage:0.9.19

WORKDIR /app

ADD . /app

RUN apt-get update && apt-get install -y --no-install-recommends python3.5 git python3-pip python3-dev postgresql postgresql-contrib build-essential nano apache2 libapache2-mod-wsgi-py3 python3-setuptools python-psycopg2 libpq-dev
RUN a2enmod wsgi
RUN pip3 install --upgrade pip
RUN pip3 install psycopg2 django==2.0.12 whoosh==2.7.4 pytz

WORKDIR /var/www/python
RUN git clone https://github.com/webis-de/corpus-viewer.git
WORKDIR /var/www/python/corpus-viewer
RUN git submodule update --recursive --remote --init

ARG setting_files=/kritten
ENV folder_setting_files=$setting_files

EXPOSE 8000
EXPOSE 80

WORKDIR /app
CMD ["python3", "app.py"]
