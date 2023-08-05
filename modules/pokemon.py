from typing import Any
from modules import cmp_table
import requests
import math


pogoapi = "https://pogoapi.net/api/v1/"

class Pokemon():
    def __init__(self, name, lvl, fast_move, charged_move, iv, is_shadow):
        self.name = name
        self.lvl = lvl
        self.fast_move = fast_move
        self.charged_move = charged_move
        self.iv = [int(stat) for stat in iv.split('-')]
        self.is_shadow = is_shadow
        self.types = []
        self.sprite = None
        self.dps = None
        self.stats = None


    def is_mega(self):
        name = self.name.split()
        if name[0].lower() == 'mega' or name[0].lower() == 'primal':
            return True
        return False


    def get_pokemon_stats(self):
        pokemon_stats = "pokemon_stats.json"
        try:
            response = requests.get(pogoapi + pokemon_stats)
            data = response.json()
            name = self.name.split()
            name_len = len(name)
            for stats in data:
                if name_len > 1:
                    if stats['pokemon_name'] == name[0].capitalize():
                        if stats['form'] == name[1].capitalize():
                            return stats
                        
                # Mewtwo wierd case (api issue with armored form)
                elif stats['pokemon_name'] == name[0].capitalize():
                    if stats['form'] == 'Normal':
                        return stats
                    
                elif stats['pokemon_name'].lower() == name[0].lower():
                    return stats
                
        except requests.exceptions.RequestException as e:
            print("Error", e)

    def get_mega_pokemon_stats(self):
        url = "mega_pokemon.json"
        response = requests.get(pogoapi + url)
        if response.ok:
            data = response.json()
            for pokemon in data:
                if pokemon['mega_name'].lower() == self.name.lower():
                    return pokemon


    def get_types(self):
        base_url = 'https://pokeapi.co/api/v2/pokemon/'

        # Due to giratina case (giratina-origin/ giratina-altered)
        name = self.name.split()
        name = ("-").join(name).lower()

        # For regular pokemon
        try:
            response = requests.get(base_url + name)
            data = response.json()
            for type in data['types']:
                self.types.append(type['type']['name'])
            
        except requests.exceptions.RequestException as e:
            print("Error", e)


    def get_mega_types(self):
        url = "mega_pokemon.json"
        response = requests.get(pogoapi + url)
        if response.ok:
            data = response.json()
            for pokemon in data:
                if pokemon['mega_name'].lower() == self.name.lower():
                    for type in pokemon['type']:
                        self.types.append(type.lower())
    

    def get_cmp(self):
        data = cmp_table.table
        for line in data:
            if float(self.lvl) == line['level']:
                return line['multiplier']


    def get_fast_move(self):
        fm = "fast_moves.json"
        response = requests.get(pogoapi + fm)
        data = response.json()
        for move in data:
            if move['name'].lower() == self.fast_move.lower():
                self.fast_move = move
                return move
        raise ValueError("No such fast move")
    

    def get_charge_move(self):
        cm = "charged_moves.json"
        response = requests.get(pogoapi + cm)
        data = response.json()
        for move in data:
            if move['name'].lower() == self.charged_move.lower():
                self.charged_move = move
                return move
        raise ValueError("No such charged move")
    

    def get_sprite(self, stats, name, is_shiny):
        pokemon_id = stats['pokemon_id']
        name = name.split()

        if name[0].lower() == 'mega':
            filename = f"{pokemon_id}-mega.png"
            for word in name:
                if word.lower() == 'x':
                    filename = f"{pokemon_id}-mega-x.png"
                elif word.lower() == 'y':
                    filename = f"{pokemon_id}-mega-y.png"
        elif name[0].lower() == 'primal':
            filename = f"{pokemon_id}-primal.png"
        elif len(name) > 1:
            filename = f"{pokemon_id}-{name[1].lower()}.png"
        else:
            filename = f"{pokemon_id}.png"

        if is_shiny:
            self.sprite = f"shiny/{filename}"
        else:    
            self.sprite = filename

                

    def calculate_dps(self, fast_move, charge_move, atk_stat, atk_iv):
        fm_power, fm_duration, fm_energy_gain, fm_type = fast_move['power'], fast_move['duration'] / 1000, fast_move['energy_delta'], fast_move['type'].lower()
        cm_power, cm_duration, cm_energy_cost, cm_type = charge_move['power'], charge_move['duration'] / 1000, charge_move['energy_delta'], charge_move['type'].lower()

        cmp = self.get_cmp()
        attack = (atk_stat + atk_iv) * cmp

        if self.is_shadow:
            SHADOW = 1.2
        else:
            SHADOW = 1
        
        # power of fast move
        if fm_type in self.types:
            FM_STAB = 1.2
        else:
            FM_STAB = 1
        fm_dmg = math.floor(0.5 * attack / 100 * fm_power * FM_STAB * SHADOW) + 1

        # power of charge move
        if cm_type in self.types:
            CM_STAB = 1.2
        else:
            CM_STAB = 1
        cm_dmg = math.floor(0.5 * attack / 100 * cm_power * CM_STAB * SHADOW) + 1

         # dps and eps of fast and charged moves
        fdps = fm_dmg / fm_duration
        feps = fm_energy_gain / fm_duration
        cdps = cm_dmg / cm_duration
        ceps = cm_energy_cost / cm_duration * -1

        dps = (fdps * ceps + cdps * feps) / (ceps + feps)
        #dps = dps0 + (cdps - fdps) / (ceps + feps) * 0.5

        self.dps = f"{dps:.2f}"
    