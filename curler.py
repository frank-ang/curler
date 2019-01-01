'''
Load Tester to make HTTP/S GET requests to a URL endpoint
Parameters are set from: 
* SSM Parameter store with prefix
* Environment variables
* 

PARAM_PREFIX : e.g. "prod.wordpress.canary." 
    base SSM Parameter namespace for "endpoint" and "sleep" variables

TPS rate maintained using tumbling window across threads within the same process.
'''
import argparse
import boto3
import logging
import multiprocessing
import os
import requests
import sys
import time
from datetime import datetime
from datetime import timedelta
import threading
from threading import Lock, Thread

TUMBLING_WINDOW_SECS = 10
lock = Lock()
g_timewindow_start = datetime.now()
g_timewindow_end = g_timewindow_start + timedelta(seconds=TUMBLING_WINDOW_SECS)
g_request_count = 0

class Client_Thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        # Main request loop for each thread
        end_time = datetime.now() + timedelta(hours=args.maxhours)
        logging.info("{}: Begin Loop. maxhours: {}, end_time: {} ".format(self.name, args.maxhours, end_time))
        
        while True:

            if (datetime.now() > end_time):
                break # Absolute hard stop after elapsed hours

            logging.debug("{}: Calling endpoint: {}".format(self.name, args.endpoint))
            resp = requests.get(args.endpoint)
            if resp.status_code != 200:
                raise ValueError("Test value error.")
            logging.info("{}: Called endpoint: {}, elapsed seconds: {}, status code: {}, reason: {}" \
                .format(self.name, args.endpoint, resp.elapsed.total_seconds(), resp.status_code, resp.reason))
            print("{{ \"endpoint\": \"{}\", \"elapsedseconds\": {}, \"status_code\": {}, \"reason\": \"{}\" }}" \
                .format( args.endpoint, resp.elapsed.total_seconds(), resp.status_code, resp.reason))

            current_time = datetime.now()
            global g_timewindow_start
            global g_timewindow_end
            global g_request_count
            lock.acquire()

            if (current_time > g_timewindow_end):
                # reset the tumbling window
                logging.debug("{}: END of Window from {} until {}".format(self.name, g_timewindow_start, g_timewindow_end))
                g_timewindow_start = g_timewindow_end
                g_timewindow_end += timedelta(seconds=TUMBLING_WINDOW_SECS)
                g_request_count = 0
            else:
                g_request_count += 1
                  
            ## Compute sleep dynamically to achieve TPS across other threads.
            time_elapsed = (current_time - g_timewindow_start).total_seconds()
            time_remaining = (g_timewindow_end - current_time).total_seconds()
            remaining_requests_all = (args.tps * TUMBLING_WINDOW_SECS) - g_request_count
            remaining_requests_this_thread = float(remaining_requests_all) / args.threads
            sleep_secs = 1
            actual_tps = g_request_count / time_elapsed
            if remaining_requests_this_thread > 0:
                sleep_secs = (time_remaining / remaining_requests_this_thread) - resp.elapsed.total_seconds()
                logging.debug("{}: time_elapsed: {}, time_remaining: {}, g_request_count: {}, remaining_requests_all: {}, actual_TPS: {}, sleep_secs: {}" \
                    .format(self.name, time_elapsed, time_remaining, g_request_count, remaining_requests_all, actual_tps, sleep_secs))
 
            lock.release()
            if sleep_secs >= 0:
                time.sleep(sleep_secs)

        logging.info("End Loop...")


def load_generation_main():
    threads = []
    for t in range(args.threads):
       threads.append(Client_Thread("Client"+str(t)))
       threads[-1].start()
    for thread in threads:
       thread.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("### Starting Load Tester ###")

    # arguments as CLI parameters
    parser = argparse.ArgumentParser(
        description="Load Tester to make HTTP/S GET requests to a URL endpoint"
    )
    parser.add_argument('--prefix', help='SSM Parameter Store prefix', required=False,
                        type=str, default='prod.wordpress.canary.', dest='param_prefix')
    parser.add_argument('--endpoint', help='The URL endpoint to be tested', required=False,
                        type=str, default='https://www.demolab.host/', dest='endpoint')
    parser.add_argument('--threads', help='Count of client threads', required=False,
                        type=int, default=2, dest='threads')
    parser.add_argument('--tps', help='Transactions per second accross threads', required=False,
                        type=int, default=1, dest='tps')
    parser.add_argument('--maxhours', help='Max time hours to run the canary', required=False,
                        type=int, default=1, dest='maxhours')
    args = parser.parse_args()

    # arguments as Environment variables, overrides above
    if (os.environ.get('PARAM_PREFIX') is not None):
        args.param_prefix = os.environ.get('PARAM_PREFIX')
    if (os.environ.get('ENDPOINT') is not None):
        args.endpoint = os.environ.get('ENDPOINT')
    if (os.environ.get('THREADS') is not None):
        args.threads = int(os.environ.get('THREADS'))
    if (os.environ.get('TPS') is not None):
        args.tps = int(os.environ.get('TPS'))
    if (os.environ.get('MAX_HOURS') is not None):
        args.maxhours = int(os.environ.get('MAX_HOURS'))

    # arguments as SSM Parameters, highest precedence
    session = boto3.session.Session()
    ssm = boto3.client('ssm', region_name='us-east-1')
    try:
        ssm_endpoint = ssm.get_parameter(Name=args.param_prefix+'endpoint')
        if (ssm_endpoint is not None):
            args.endpoint = ssm_endpoint['Parameter']['Value']
            logging.info ("SSM: endpoint: %s" % (args.endpoint))
        ssm_threads = ssm.get_parameter(Name=args.param_prefix+'threads')
        if (ssm_threads is not None):
            args.threads = int(ssm_threads['Parameter']['Value'])
            logging.info ("SSM threads: %s" % (args.threads))
        ssm_tps = ssm.get_parameter(Name=args.param_prefix+'tps')
        if (ssm_tps is not None):
            args.tps = int(ssm_tps['Parameter']['Value'])
            logging.info ("SSM tps: %s" % (args.tps))
        ssm_max_hours = ssm.get_parameter(Name=args.param_prefix+'max_hours')
        if (ssm_max_hours is not None):
            args.maxhours = float(ssm_max_hours['Parameter']['Value'])
            logging.info ("SSM maxhours: %s" % (args.maxhours))
    except Exception as e:
        logging.error(e, exc_info=True)
        pass
    if (args.maxhours < 0):
        args.maxhours = 24 * 365 # 1year limit

    logging.info ("args: {}".format(args))
    try: 
        load_generation_main()
    except Exception as e:
        parser.print_help()
        raise    