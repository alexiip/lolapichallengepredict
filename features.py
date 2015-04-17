#-----------------------------------------------------------------------------
# Name: get_matches.py
#
# Author: Alexander Popov
#
#-----------------------------------------------------------------------------  
import os
import sys
import json

import TeamFeatures

#Debug flag to only process ~100 rows 
debug = False
#Use all of the data for the training set, no test set is created
train_only = True

version = 10
matches_data_file = r'E:\RiotApiChallenge\Data\matches.tsv'
features_file_train = r'E:\RiotApiChallenge\Data\features_train_{0}.tsv'.format(version)
features_file_test = r'E:\RiotApiChallenge\Data\features_test_{0}.tsv'.format(version)
features_file_champ = r'E:\RiotApiChallenge\Data\features_champ_{0}.tsv'.format(version)

count = 0
write_header = True

num_rows = 0

epochs = []
train_split_epoch = 0

champ_features = {}
champ_ban_features = {}

print("Generating features...")

with open(matches_data_file, 'r') as f:
    for line in f:
        epoch = line.split('\t')[0]
        epochs.append(epoch)
        
        num_rows += 1  
        
        count += 1
    
        if debug:
            if count == 100:
               break

count = 0               

print('Total rows to process: {0}'.format(num_rows))

#Split train and test by time
epochs.sort()

if train_only:
    train_split_epoch = epochs[int(num_rows)-1]
else:
    train_split_epoch = epochs[int(num_rows*.8)]

#generate champion features on train data
with open(matches_data_file, 'r') as f:
    next(f)
    for line in f:
        line_arr = line.split('\t')
        epoch = line_arr[0]
        
        #only generate champ stats for train data set
        if epoch > train_split_epoch:
            break
        
        stats = {}
        ban_stats = {}
        winner = 0
        
        j = ''
        try:
            j = json.loads(line_arr[2])
        except:
            continue
        
        #create champion ban stats features
        for team in j['teams']:
            
            team_id = team.get('teamId', 1)
            
            #TODO fix label being set multiple times
            #set winning team label
            if team.get('winner', False) == True:
                winner = team_id
            
            if team.get('bans', -1) == -1:
                break
            for ban in team['bans']:
                champ = ban.get('championId', "-1")
                ban_stats = champ_ban_features.get(champ, {})
                if bool(ban_stats):
                    if team_id == winner:
                        ban_stats["bans"] = ban_stats["bans"] + 1
                    ban_stats["total"] = ban_stats["total"] + 1
                else:
                    if team_id == winner:
                        ban_stats["bans"] = 1
                    else:
                        ban_stats["bans"] = 0
                    ban_stats["total"] = 1
            
                champ_ban_features[champ] = ban_stats 
            
        #create champion stats features
        for part in j['participants']:
            team = part.get('teamId', "-1")
            
            #TODO fix label being set multiple times
            #set winning team label
            if part['stats'].get('winner', "-1") == True:
                winner = team
            
            if team == -1:
                break
            
            champ = part.get('championId', "-1")
            lane = part['timeline'].get('lane', "-1")
           
            #update champ statistics
            stats = champ_features.get(champ, {})
            if bool(stats):
                #find opponent and compute winning statistics
                # for opponent in j['participants']:
                    # opp_lane = opponent['timeline'].get('lane', "-1")
                    # if opponent.get('teamId', -1) != team or lane != opp_lane:
                        # continue
                    # opp_champ = opponent.get('championId', "-1")
                    # if team == winner:
                        # opp_wins = stats['won_against_opponents'].get(opp_champ,{}).get('wins', 0)
                        # opp_total = stats['won_against_opponents'].get(opp_champ,{}).get('total', 0)
                        # if opp_wins == 0 and opp_total == 0:
                            # stats['won_against_opponents'][opp_champ] = {}
                        # stats['won_against_opponents'][opp_champ]['wins'] = opp_wins + 1
                        # stats['won_against_opponents'][opp_champ]['total'] = opp_total + 1
                    # else:
                        # opp_wins = stats['won_against_opponents'].get(opp_champ,{}).get('wins', 0)
                        # opp_total = stats['won_against_opponents'].get(opp_champ,{}).get('total', 0)
                        # if opp_wins == 0 and opp_total == 0:
                            # stats['won_against_opponents'][opp_champ] = {}
                        # stats['won_against_opponents'][opp_champ]['wins'] = opp_wins
                        # stats['won_against_opponents'][opp_champ]['total'] = opp_total + 1 
                
                if team == winner:
                    stats["wins"] = stats["wins"] + 1
                stats["total"] = stats["total"] + 1
                #compute most played lane for the champion since this data is unavailable in
                #current-game-v1.0, we will use this data for online-prediction to estimate opponent
                if stats["lanes"].get(lane, "-1") != "-1":
                    stats["lanes"][lane] = stats["lanes"][lane] + 1
                else:
                    stats["lanes"][lane] = 1
            else:
                if team == winner:
                    stats["wins"] = 1
                else:
                    stats["wins"] = 0
                stats["total"] = 1
                stats["lanes"] = {}
                stats["won_against_opponents"] = {}
            
            champ_features[champ] = stats
            
        count += 1
        print 'Progress 1/2: {0}%\r'.format(str(int((float(count)/int(num_rows*.8))*100))) ,
        
        if debug:
            if count == 100:
               break
count = 0

#compute most played lane for champion
pref_lane = {}
for champ, stats in champ_features.iteritems():
    if stats.get('lanes', {}) != {}:
        pref_lane[champ]=max(stats['lanes'].iterkeys(), key=(lambda key: stats['lanes'][key]))

#Write champion features to file
with open(features_file_champ, 'w') as f:
    #champion stats
    json.dump(champ_features, f)
    f.write('\t')
    #banned champion stats
    json.dump(champ_ban_features, f)
    f.write('\t')
    #champion pref lane
    json.dump(pref_lane, f)
    

#raw_input("Press Enter to continue...")
print('Part one completed...')

with open(matches_data_file, 'r') as f:
    next(f)
    for match in f:
        line_arr = match.split('\t')
        
        epoch = line_arr[0]
        
        j = ''
        try:
            j = json.loads(line_arr[2]) 
        except:
            continue
        
        #label
        winner = ""
        
        #features
        t1 = TeamFeatures.TeamFeatures(1)
        t2 = TeamFeatures.TeamFeatures(2)
        
        #create features
        part_team = 1
        
        #team features
        for team_data in j['teams']:
            team = team_data.get('teamId', 1)
            if team == 100:
                part_team = t1
            else:
                part_team = t2
            
            #banned champion features
            if team_data.get('bans', -1) != -1:
                part_team.banned_champs_vals = []
                banned = 0
                for ban in team_data['bans']:
                    champ = ban.get('championId', '0')
                    pick_turn = ban.get('pickTurn', '0')
                    ban_rate = float(champ_ban_features.get(champ, {}).get('bans', 0))/champ_ban_features.get(champ, {}).get('total', 1)
                                        
                    part_team.banned_champs_vals.append(str(champ))
                    #part_team.banned_champs_vals.append(str(pick_turn))
                    part_team.banned_champs_vals.append(str(ban_rate))
                    
                    banned += 1
                
                while banned < 3:
                    #champ
                    part_team.banned_champs_vals.append('0')
                    #ban rate
                    part_team.banned_champs_vals.append('0')
                    banned +=1
        
        #summoner features
        for part in j['participants']:
            team = part.get('teamId', -1)
            
            #TODO fix label being set multiple times
            #set winning team label
            if part['stats'].get('winner', "-1") == True:
                winner = team
            
            if team == -1:
                break
            
            if team == 100:
                part_team = t1
            else:
                part_team = t2
            
            
            #create features for each team using the participants
            p_id = int(part.get('participantId')) 
            
            #assign ids 1-5 for team 2 for easier feature assignment
            p_id = p_id - 1 if p_id < 6 else p_id - 5 - 1
            
            #print(part)
            part_team.summoners[p_id].Role=part['timeline'].get('role', "-1")
            
            lane = part['timeline'].get('lane', "-1")
            part_team.summoners[p_id].Lane=lane
            
            c_id = part.get('championId', "-1")
            part_team.summoners[p_id].Champion=c_id
            part_team.summoners[p_id].Tier=part.get('highestAchievedSeasonTier', "-1")
            part_team.summoners[p_id].Spell1=part.get('spell1Id', "-1")
            part_team.summoners[p_id].Spell2=part.get('spell2Id', "-1")
            
            
            win_rate = float(champ_features.get(c_id, {}).get('wins', 0))/champ_features.get(c_id, {}).get('total', 1)
            part_team.summoners[p_id].ChampionWinRate=win_rate
            
            #opponent
            # win_rate_against_opp = 0
            # for opponent in j['participants']:
                # opp_lane = opponent['timeline'].get('lane', "-1")
                # if opponent.get('teamId', -1) != team or lane != opp_lane:
                    # continue
                # opp_champ = opponent.get('championId', "-1")
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
                    rune_rank = r.get('rank', "0")
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
        
        #writer header the first time
        if write_header:
            with open(features_file_train, 'w') as f:
                f.write('\t'.join(['EpochSeconds', "Winner"])\
                        +'\t' + '\t'.join([t1.print_header(), t2.print_header()]) +'\n')
            
            with open(features_file_test, 'w') as f:
                f.write('\t'.join(['EpochSeconds', "Winner"])\
                        +'\t' + '\t'.join([t1.print_header(), t2.print_header()]) +'\n')

            write_header = False
            
        #write feature line
        if epoch <= train_split_epoch: 
            with open(features_file_train, 'a') as f:
                    f.write('\t'.join([epoch, str(winner)])\
                            +'\t'+ '\t'.join([t1.print_summoner_values(), t2.print_summoner_values()])+'\n')
        else:
             with open(features_file_test, 'a') as f:
                    f.write('\t'.join([epoch, str(winner)])\
                            +'\t'+ '\t'.join([t1.print_summoner_values(), t2.print_summoner_values()])+'\n')
       
        count+=1
        if debug:
            if count == 100:
               break
               
        print 'Progress 2/2: {0}%\r'.format(str(int((float(count)/num_rows)*100))) ,
        
                
