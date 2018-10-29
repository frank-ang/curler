import argparse
import os
import sys
import time
import requests

MAX_LOOPS=3
SLEEP_SECS=1

def canary_main(endpoint):
    print ("Canary Main...")
    print ("Begin Loop...")
    for i in range(MAX_LOOPS):
        if i>0: # don't sleep on the first iteration.
            time.sleep(SLEEP_SECS) # no jitter
        print("do stuff.")
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

    

