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
from datetime import datetime, timedelta

_API_BUCKET_TIME_SECONDS = 5*60

_CALLS_LIMIT_SHORT = 10
_CALLS_TIME_LIMIT_SHORT_SECONDS = 10
_CALLS_LIMIT_LONG_ = 500
_CALLS_TIME_LIMIT_LONG_MINUTES = 10

#Enter your timezone offset here
local_timezone_hours_offset = -7 * -1

region = 'na'
url = 'https://na.api.pvp.net/api/lol/{0}/v4.1/game/ids?api_key={1}&beginDate={2}'
#Enter your Riot API Key here
key = ''

games_data_file = r'E:\RiotApiChallenge\Data\games.tsv'

def get_current_epoch_time(t=(datetime.now()+timedelta(hours=local_timezone_hours_offset))):
    return int((t-datetime(1970,1,1)).total_seconds())

def get_games(epoch_time):

    r = requests.get(url.format(region,key, epoch_time))

    return r.text.replace('[','').replace(']','')

def get_all_games(start_epoch_time):
    calls_short = 0
    calls_long = 0
    start_time_short = datetime.now()
    start_time_long = datetime.now()
    
    epoch_time = start_epoch_time
    
    #write header
    with open(games_data_file, 'w') as f:
        f.write('\t'.join(['EpochSeconds','Games', '\n']))
        
    #loop to get games via challenge api
    while True:
        current_epoch_time = get_current_epoch_time()
        #print(current_epoch_time)
        if epoch_time >= current_epoch_time:
            print("Sleeping at the end for seconds: {0}".format(str(_API_BUCKET_TIME_SECONDS)))
            time.sleep(_API_BUCKET_TIME_SECONDS)
            #continue
        
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
        games = get_games(epoch_time)
        
        if games:
            line = '\t'.join([str(epoch_time), games])
            
            print('Epoch: {0}, Games: {1}'.format(epoch_time, games))
            if 'Not Found' not in games:
                with open(games_data_file, 'a') as f:
                    f.write(line+'\n')
                epoch_time += _API_BUCKET_TIME_SECONDS
        else:
            epoch_time += _API_BUCKET_TIME_SECONDS
        
        #update call count
        calls_short += 1
        calls_long += 1
        
        #if calls_short == 4:
        #    return
    

if __name__ == "__main__":   
    #1427866800
    t = datetime(2015, 04, 01, 05, 25)

    epoch_time = 0
    if len(sys.argv) > 1:
        epoch_time = int(sys.argv[1])
    else:
        epoch_time = get_current_epoch_time(t)
    
    print('Starting time: ' + str(epoch_time))
       
    get_all_games(epoch_time)    