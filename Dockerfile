FROM python:3.5

MAINTAINER kizi "stanislav.vojir@gmail.com"

RUN mkdir /easyminer-evaluation

RUN pip install pandas && \
    pip install requests

ADD / /easyminer-evaluation

WORKDIR /easyminer-evaluation

#CMD [ "python", "./easyminercenter_api.py" ]