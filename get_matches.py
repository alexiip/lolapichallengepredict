#-----------------------------------------------------------------------------
# Name: get_matches.py
#
# Author: Alexander Popov
#
#-----------------------------------------------------------------------------  

import requests
import os
import logging
import time
import sys
from datetime import datetime

_API_BUCKET_TIME_SECONDS = 5*60

_CALLS_LIMIT_SHORT = 900
_CALLS_TIME_LIMIT_SHORT_SECONDS = 10
_CALLS_LIMIT_LONG_ = 50000
_CALLS_TIME_LIMIT_LONG_MINUTES = 10

region = 'na'
url = 'https://na.api.pvp.net/api/lol/{0}/v2.2/match/{1}?api_key={2}'
key = ''

matches_data_file = r'E:\RiotApiChallenge\Data\matches.tsv'
games_data_file = r'E:\RiotApiChallenge\Data\games.tsv'

def get_current_epoch_time(t=datetime.now()):
    return int((t-datetime(1970,1,1)).total_seconds())

def get_match(match_id):

    #print(time)
    #print(epoch_time)
    r = requests.get(url.format(region,match_id,key))
    #print(r.url)

    #print(r.text)
    return r.text

def get_all_games(start_epoch_time):
    calls_short = 0
    calls_long = 0
    start_time_short = datetime.now()
    start_time_long = datetime.now()
    
    #write header
    #with open(matches_data_file, 'w') as f:
    #    f.write('\t'.join(['EpochSeconds','MatchId', 'MatchDataJSON', '\n']))

    #begin loop to read files
    with open(games_data_file, 'r') as f:
        next(f)
        for line in f:
            line_arr = line.split('\t')
            processing_epoch = line_arr[0]
            
            if int(processing_epoch) < start_epoch_time:
                continue
            
            match_ids = line_arr[1]
            for match_id in match_ids.split(','):                  
                #check for rate limit  
                if calls_short == _CALLS_LIMIT_SHORT and int((datetime.now() - start_time_short).total_seconds()) <= _CALLS_TIME_LIMIT_SHORT_SECONDS:
                    print("Sleeping due to call limit for seconds: {0}".format(str(_CALLS_LIMIT_SHORT)))
                    time.sleep(_CALLS_LIMIT_SHORT)
                    start_time_short = datetime.now()
                    calls_short = 0
                elif int((datetime.now() - start_time_short).total_seconds()) > _CALLS_TIME_LIMIT_SHORT_SECONDS:
                    start_time_short = datetime.now()
                    calls_short = 0

                if calls_long == _CALLS_LIMIT_LONG_ and int((datetime.now() - start_time_long).total_seconds()) <= _CALLS_TIME_LIMIT_LONG_MINUTES * 60:
                    print("Sleeping due to call limit for seconds: {0}".format(str(_CALLS_TIME_LIMIT_LONG_MINUTES * 60)))
                    time.sleep(_CALLS_TIME_LIMIT_LONG_MINUTES * 60)
                    start_time_long = datetime.now()
                    calls_long = 0
                elif int((datetime.now() - start_time_long).total_seconds()) > _CALLS_TIME_LIMIT_LONG_MINUTES * 60:
                    start_time_long = datetime.now()
                    calls_long = 0  
                    
                #actual code
                match = get_match(match_id)
                
                if match:
                    write_line = '\t'.join([processing_epoch, match_id, match])
                    print('Processing Epoch: {0}, Match: {1}'.format(processing_epoch, match_id))
                    if 'Not Found' not in match:
                        with open(matches_data_file, 'a') as w:
                            w.write(write_line+'\n')
                
                #update call count
                calls_short += 1
                calls_long += 1
                
                #if calls_short == 4:
                #    return
            
if __name__ == "__main__":   
    #1427866800
    t = datetime(2015, 04, 01, 05, 25)

    start_epoch_time = 0
    if len(sys.argv) > 1:
       start_epoch_time = int(sys.argv[1])
    else:
       start_epoch_time = get_current_epoch_time(t)
    
    print('starting time: ' + str(start_epoch_time))
       
    get_all_games(start_epoch_time)    