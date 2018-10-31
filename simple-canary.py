'''
Canary to make http requests to an endpoint
Environment parameters: 
'''
import argparse
import os
import sys
import time
import requests
from datetime import datetime
from datetime import timedelta

def canary_main():
    print ("Canary Main...")

    end_time=datetime.now() + timedelta(hours=args.maxhours)

    print ("Begin Loop...")
    while True:
        if datetime.now() > end_time:
            break
        print("Calling endpoint: " + args.endpoint)
        resp = requests.get('http://' + args.endpoint + '/')
        print (resp)
        time.sleep(args.sleep) # TODO add jitter
    print ("End Loop...")

if __name__ == '__main__':
    print("starting...")

    description = '''Simple Canary.'''
    parser = argparse.ArgumentParser(
        description=description
    )
    parser.add_argument('--endpoint', help='The API endpoint', required=False,
                        type=str, default='aws.amazon.com', dest='endpoint')
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

    

