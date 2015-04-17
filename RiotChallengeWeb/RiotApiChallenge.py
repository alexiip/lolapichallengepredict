#-----------------------------------------------------------------------------
# Name: get_matches.py
#
# Author: Alexander Popov
#
#-----------------------------------------------------------------------------  
import time
import requests
import json
import logging

import TeamFeatures

SUMMONER_NOT_FOUND = -1
ERROR = -2

champ_features_file = 'features_champ_10.tsv'

#Insert your RiotAPI key here
key = ''
curr_game_url = 'https://na.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/{0}/{1}?api_key={2}'
summ_name_url = 'https://na.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}'
summ_league_url = 'https://na.api.pvp.net/api/lol/{0}/v2.5/league/by-summoner/{1}/entry?api_key={2}'

#Insert your AzureML key here
azure_key = ''
#Insert your AzureML API url here
azure_ml_api_url = 'https://ussouthcentral.services.azureml.net/workspaces/9cc892d0247042b5b47daaf7e8fe0817/services/aabcacd5c5cc47b5beb681110fead665/execute?api-version=2.0&details=true'

#Call AzureML to make prediction
def make_prediction(curr_game, summ_id):
    
    header, values = get_features(curr_game, summ_id)
    header_arr = header.split(',')
    values_arr = values.split(',')

    #have to add a bogus column because of a mistake made in uploading features, this does not impact model accuracy
    payload = {"Inputs": {                                      
                "RAPC_in":                                       
               {                                                
                    "ColumnNames": header_arr+["Column 3634"],    
                    "Values": [values_arr+['0'],]
               },        },
            "GlobalParameters": {}
            }
    payload = str.encode(json.dumps(payload))#.replace('Tier', 'Tear')
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ azure_key)}
    r = None
    try:
        r = requests.post(azure_ml_api_url, data= payload, headers = headers)
    except Exception, e:
        logging.error(e)
        return -1
    
    if r.status_code == 200:
        winner = r.json()['Results']['RAPC_out']['value'].get('Values', -1)[0][3614]
        confidence = r.json()['Results']['RAPC_out']['value'].get('Values', -1)[0][3615]
        summ_team = get_summ_team(curr_game, summ_id)
                
        if int(summ_team) == int(winner):
            won = True
        else:
            won = False
        return won, confidence
    else:
        logging.error(r.text)
        return -1

def get_summ_team(curr_game, summ_id):
    for part in curr_game['participants']:
        part_id = part.get('summonerId', -1)
        if int(part_id) == int(summ_id):
            return part.get('teamId', -1)
    return -1
        
def get_current_game(summoner, region='NA1'):
    summ_id = get_summoner_id(summoner)
    url = curr_game_url.format(region, summ_id, key)
    r = None
    try:
        r = requests.get(url)        
    except Exception, e:
        logging.error(e)
        return ERROR, ERROR
    
    if r.status_code == 200:
        return r.json(), summ_id
    else:
        return SUMMONER_NOT_FOUND, SUMMONER_NOT_FOUND

def get_summoner_id(summoner, region='na'):
    url = summ_name_url.format('na', summoner, key)
    r = None
    try:
        r = requests.get(url)        
    except:
        return ERROR

    if r.status_code == 200:
        return r.json().get(summoner, {}).get('id', ERROR)
    else:
        return SUMMONER_NOT_FOUND
        
def get_summoner_tier(summ_id, region):
    #we assume the summoner is playing in soloQ since we dont have any other info
    QUEUE_TYPE = 'RANKED_SOLO_5x5'
    
    
    url = summ_league_url.format('na', summ_id, key)
    r = None
    try:
        r = requests.get(url)        
    except:
        return ERROR
    
    if r.status_code == 200:
        tear = ''
        for league in r.json().get(summ_id, {}):
            if league.get('queue', '') == QUEUE_TYPE:
                return league.get('tier', '')
    else:
        return SUMMONER_NOT_FOUND
        
def get_features(curr_game, summ_id, region = 'na'):
    champ_features = {}
    champ_ban_features = {}
    champ_lane = {}
    
    #read in pre computed champion features
    with open(champ_features_file, 'r') as f:
        for line in f:
            line_arr = line.split('\t')
            champ_features = eval(line_arr[0])
            champ_ban_features = eval(line_arr[1])
            champ_lane = eval(line_arr[2])
            #print(champ_features)
    j = curr_game
    
    #label
    winner = 100
    
    #features
    t1 = TeamFeatures.TeamFeatures(1)
    t2 = TeamFeatures.TeamFeatures(2)
    
    #create features
    part_team = 1
    
    #team features
    banned = 0
    for ban in j['bannedChampions']:
        team = ban.get('teamId', 1)
        if team == 100:
            part_team = t1
        else:
            part_team = t2
        
        #banned champion features
        part_team.banned_champs_vals = []
                
        champ = ban.get('championId', '0')
        pick_turn = ban.get('pickTurn', '0')
        ban_rate = float(champ_ban_features.get(str(champ), {}).get('bans', 0))/champ_ban_features.get(str(champ), {}).get('total', 1)
                            
        part_team.banned_champs_vals.append(str(champ))
        #part_team.banned_champs_vals.append(str(pick_turn))
        part_team.banned_champs_vals.append(str(ban_rate))
        
        if team == 100:
            t1 = part_team
        else:
            t2 = part_team
        
        banned += 1

    #fill in missing values
    while len(t1.banned_champs_vals) < 6:
        t1.banned_champs_vals.append('0')

    while len(t2.banned_champs_vals) < 6:
        t2.banned_champs_vals.append('0')
    #summoner features
    p_id_t1 = 0
    p_id_t2 = 0
    for part in j['participants']:
        #if part.get('summonerId', -1) != player_id:
        #    continue
        team = part.get('teamId', -1)
               
        if team == 100:
            part_team = t1
            p_id = p_id_t1
            p_id_t1 +=1
        else:
            part_team = t2
            p_id = p_id_t2
            p_id_t2 += 1
                     
        #print(part)
        #part_team.summoners[p_id].Role=part['timeline'].get('role', "-1")
        c_id = part.get('championId', "-1")
        part_team.summoners[p_id].Champion=c_id
        
        lane = champ_lane.get(str(c_id), "-1")
        part_team.summoners[p_id].Lane=lane
        
        tier = get_summoner_tier(str(summ_id), region)
        part_team.summoners[p_id].Tier=part.get(tier, "-1")
        part_team.summoners[p_id].Spell1=part.get('spell1Id', "-1")
        part_team.summoners[p_id].Spell2=part.get('spell2Id', "-1")
        
        
        win_rate = float(champ_features.get(str(c_id), {}).get('wins', 0))/champ_features.get(str(c_id), {}).get('total', 1)
        part_team.summoners[p_id].ChampionWinRate=win_rate
        
        # #opponent
        # win_rate_against_opp = 0
        # for opponent in j['participants']:
            # opp_champ = opponent.get('championId', "-1")
            # opp_lane = champ_lane.get(str(opp_champ), "-1")
            # if opponent.get('teamId', -1) != team or lane != opp_lane:
                # continue
            # wins_against_opp = champ_features.get(c_id, {}).get('won_against_opponents', {}).get(opp_champ, {}).get('wins', 0)
            # total_against_opp = champ_features.get(c_id, {}).get('won_against_opponents', {}).get(opp_champ, {}).get('total', 0)
            # win_rate_against_opp = float(wins_against_opp)/total_against_opp if total_against_opp > 0 else 0
            # #TODO: need better way to estimate for now pick the first one in case there are two or more
            # break
            
        # part_team.summoners[p_id].AgainstOpponentChampWinRate = win_rate_against_opp
        
        #runes
        rune_id = '-1'
        rune_rank = '0'
        if part.get('runes', -1) != -1:
            for r in part['runes']:
                rune_id = r.get('runeId', "-1")
                #rank is called count in current_game api
                rune_rank = r.get('count', "0")
                if rune_id != "-1" and rune_rank != "0":
                    part_team.summoners[p_id].runes[str(rune_id)] = str(rune_rank)
                    
        mastery_id = "-1"
        mastery_rank = "0"
        #masteris
        if part.get('masteries', -1) != -1:
            for m in part['masteries']:
                mastery_id = m.get('masteryId', "-1")
                mastery_rank = m.get('rank', "0")
                if mastery_id != "-1" and mastery_rank != "0":
                    part_team.summoners[p_id].masteries[str(mastery_id)] = str(mastery_rank)
        
        #re-assign updated values to each team
        if team == 100:
            t1 = part_team
        else:
            t2 = part_team
                
    return ','.join(['EpochSeconds', "Winner"])\
                    +',' + ','.join([t1.print_header(), t2.print_header()]), \
            ','.join([str(1), str(winner)])\
                        +','+ ','.join([t1.print_summoner_values(), t2.print_summoner_values()])