#-----------------------------------------------------------------------------
# Name: get_matches.py
#
# Author: Alexander Popov
#
#-----------------------------------------------------------------------------  
from collections import OrderedDict

import Definitions

class Summoner(object):
        
    def __init__(self, id):
        self.id = "-1"

        self.Role = "-1"
        self.Lane = "-1"
        self.Champion = "-1"
        self.Tier = "-1"
        self.Spell1 = "-1"
        self.Spell2 = "-1"

        self.ChampionWinRate = "-1"
        self.AgainstOpponentChampWinRate = "-1"
        
        self.masteries = OrderedDict()
        self.runes = OrderedDict()
        self.id = id
        d = Definitions.Definitions()
        self.runes = OrderedDict(d.get_rune_definitions())
        self.masteries = OrderedDict(d.get_masteries_definitions())
    
    def __repr__(self):
        return get_variables_str()
      
    def get_variables_str(self):
        rune_values = []
        for key in sorted(self.runes.keys()):
            rune_values.append(self.runes[key])
        rune_values_str = ','.join(rune_values)
        
        mastery_values = []
        for key in sorted(self.masteries.keys()):
            mastery_values.append(self.masteries[key])
        
        mastery_values_str = ','.join(mastery_values)
        
        return ','.join([str(self.Role), str(self.Lane), str(self.Champion), \
                 str(self.Tier), str(self.Spell1), str(self.Spell2), str(self.ChampionWinRate), \
                   #str(self.AgainstOpponentChampWinRate),\
                   mastery_values_str, rune_values_str])
    
    def get_variables_names_str(self):
        rune_names = []
        for key in sorted(self.runes.keys()) :
            rune_names.append('Rune_'+key)
        rune_names_str = ','.join(rune_names)
        
        mastery_names = []
        for key in sorted(self.masteries.keys()) :
            mastery_names.append('Mastery_'+key)
        
        
        mastery_names_str = ','.join(mastery_names)
        
        return ','.join(['Role', 'Lane', 'Champion', \
                        'Tier', 'Spell1', 'Spell2', 'ChampionWinRate',
                        # 'AgainstOpponentChampWinRate',\
                        mastery_names_str, rune_names_str])
    
class TeamFeatures(object):
    
    def __init__(self, id):
        self.summoners = [Summoner(count) for count in xrange(5)]
        self.id = id
        self.banned_champs_header = []
        self.banned_champs_vals = []
        for count in xrange(3):
            champ_count = count + 1
            self.banned_champs_header.append('Team{0}BannedChamp{1}'.format(id, champ_count))
            #self.banned_champs_header.append('Team{0}BannedChamp{1}PickTurn'.format(id, champ_count))
            self.banned_champs_header.append('Team{0}BannedChamp{1}BanRate'.format(id, champ_count))
        
        for count in xrange(6):
            self.banned_champs_vals.append('0')
        
    def print_summoner_values(self):
        s_vars = []
        
        for banned_value in self.banned_champs_vals:
            s_vars.append(banned_value)
        
        for s in self.summoners:
            s_vars.append(s.get_variables_str())
            
        return ','.join(s_vars)
    
    def print_header(self):
        s_header = []
        
        for banned_header in self.banned_champs_header:
            s_header.append(banned_header)
        
        i=1
        for s in self.summoners:
            for v in s.get_variables_names_str().split(','):
                s_header.append('Team{0}Summoner{1}{2}'.format(self.id,i,v))
            i+=1
            
        return ','.join(s_header)
        