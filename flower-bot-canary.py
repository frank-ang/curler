'''
Canary for flower ordering chat API with TranslateBot 

Sample API request: 
{
     "userid":"foo",
      "intent":"I would like to order flowers"
}

'''
import os
import sys
import time
from datetime import datetime
from datetime import timedelta
import argparse
import requests
import re
from aws_requests_auth.aws_auth import AWSRequestsAuth
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

def call_api():
    p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
    m = re.search(p,args.endpoint)
    hostname = m.group('host')
    auth = BotoAWSRequestsAuth(aws_host=hostname,
                           aws_region='us-east-1',
                           aws_service='execute-api')
    payload = {'userid':'abc123', 'intent':'I would like to buy flowers.'}
    response = requests.post(args.endpoint, auth=auth, json=payload)
    print(response.content)

def canary_main():
    end_time=datetime.now() + timedelta(hours=args.maxhours)
    while True:
        if datetime.now() > end_time:
            break
        call_api()
        time.sleep(args.sleep)

if __name__ == '__main__':
    print("starting...")

    description = '''Flower Bot Canary.'''
    parser = argparse.ArgumentParser(
        description=description
    )
    parser.add_argument('--endpoint', help='The API endpoint URL', required=False,
                        type=str, default='https://hf4bwbbphd.execute-api.us-east-1.amazonaws.com/TEST/flowers', dest='endpoint')
    parser.add_argument('--sleep', help='Sleep time secs between calls', required=False,
                        type=int, default=60, dest='sleep')
    parser.add_argument('--maxhours', help='Max time hours to run the canary', required=False,
                        type=int, default=1, dest='maxhours')

    args = parser.parse_args()

    if (os.environ.get('ENDPOINT') is not None):
        args.endpoint = os.environ.get('ENDPOINT')
    if (os.environ.get('SLEEP') is not None):
        args.sleep = int(os.environ.get('SLEEP'))
    if (os.environ.get('MAX_HOURS') is not None):
        args.maxhours = int(os.environ.get('MAX_HOURS'))

    print ("endpoint: %s" % (args.endpoint))
    print ("sleep: %s secs" % (args.sleep))
    print ("maxhours: %s hours" % (args.maxhours))
    
    # parser.print_help()
    canary_main()
    print ("Canary Ended.")

    

