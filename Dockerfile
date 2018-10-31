FROM python:3.6-alpine

ADD simple-canary.py /

RUN apk update && apk add wget && apk add py-pip && rm -rf /var/cache/apk/*
RUN pip install requests

# run python with unbuffered output
CMD [ "python", "-u", "./simple-canary.py" ]
