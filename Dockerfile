FROM python:3.6-alpine

ADD curler.py /

RUN apk update && apk add wget && apk add py-pip && rm -rf /var/cache/apk/*
RUN pip install requests
RUN pip install aws-requests-auth
RUN pip install boto3

# run python with unbuffered output
CMD [ "python", "-u", "./curler.py" ]