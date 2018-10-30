import argparse
import os
import sys
import time
import requests
from datetime import datetime
from datetime import timedelta

SLEEP_SECS=10
MAX_HOURS=1
MAX_LOOPS=60*60*MAX_HOURS/SLEEP_SECS

def canary_main(endpoint):
    print ("Canary Main...")

    end_time=datetime.now() + timedelta(hours=MAX_HOURS)

    print ("Begin Loop...")

    while true:
        if datetime.now() > end_time:
            break
        if i>0: # don't sleep on the first iteration.
            time.sleep(SLEEP_SECS) # no jitter
        print("Calling endpoint: " + endpoint)
        resp = requests.get('https://' + endpoint + '/')
        print (resp)

    print ("End Loop...")

if __name__ == '__main__':

    description = '''Simple Canary.'''
    parser = argparse.ArgumentParser(
        description=description
    )
    parser.add_argument('-endpoint', help='The API endpoint', required=False,
                        type=str, default='aws.amazon.com', dest='endpoint')
    parser.add_argument('-sleep', help='Sleep time ms between calls', required=False,
                        type=str, default='aws.amazon.com', dest='endpoint')

    args = parser.parse_args()

    if (os.environ.get('ENDPOINT') is not None):
        args.endpoint = os.environ.get('ENDPOINT')

    print ("endpoint: " + args.endpoint)
    
    # parser.print_help()
    canary_main(args.endpoint)

    

