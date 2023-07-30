from modules import cmp_table
import requests
import math


pogoapi = "https://pogoapi.net/api/v1/"

class Pokemon():
    def __init__(self, name, lvl, fast_move, charge_move, iv, is_shadow):
        self.name = name
        self.lvl = lvl
        self.fast_move = fast_move
        self.charge_move = charge_move
        self.iv = [int(stat) for stat in iv.split('-')]
        self.is_shadow = is_shadow


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


    def get_types(self):
        base_url = 'https://pokeapi.co/api/v2/pokemon/'
        name = self.name.split()
        name = ("-").join(name).lower()

        try:
            r = requests.get(base_url + name)
            data = r.json()
            types = list()
            for type in data['types']:
                types.append(type['type']['name'])
            return types
        except requests.exceptions.RequestException as e:
            print("Error", e)
    

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
                return move
        raise ValueError("No such fast move")
    

    def get_charge_move(self):
        cm = "charged_moves.json"
        response = requests.get(pogoapi + cm)
        data = response.json()
        for move in data:
            if move['name'].lower() == self.charge_move.lower():
                return move
        raise ValueError("No such fast move")
    

    def get_sprite(self, stats, name, is_shiny):
        pokemon_id = stats['pokemon_id']
        name = name.split()
        if len(name) > 1:
            filename = f"{pokemon_id}-{name[1].lower()}.png"
        else:
            filename = f"{pokemon_id}.png"

        if is_shiny:
            return f"static/sprites/pokemon/shiny{filename}"
        return f"static/sprites/pokemon/{filename}"

                

    def calculate_dps(self, fast_move, charge_move, types, atk_stat, atk_iv):
        fm_power, fm_duration, fm_energy_gain, fm_type = fast_move['power'], fast_move['duration'] / 1000, fast_move['energy_delta'], fast_move['type'].capitalize()
        cm_power, cm_duration, cm_energy_cost, cm_type = charge_move['power'], charge_move['duration'] / 1000, charge_move['energy_delta'], charge_move['type'].capitalize()

        types = self.get_types()
        cmp = self.get_cmp()
        attack = (atk_stat + atk_iv) * cmp

        if self.is_shadow:
            SHADOW = 1.2
        else:
            SHADOW = 1
        
        # power of fast move
        if fm_type in types:
            STAB = 1.2
        else:
            STAB = 1
        fm_dmg = math.floor(0.5 * attack / 100 * fm_power * STAB * SHADOW) + 1

        # power of charge move
        if cm_type in types:
            STAB = 1.2
        else:
            STAB = 1
        cm_dmg = math.floor(0.5 * attack / 100 * cm_power * STAB * SHADOW) + 1

         # dps and eps of fast and charged moves
        fdps = fm_dmg / fm_duration
        feps = fm_energy_gain / fm_duration
        cdps = cm_dmg / cm_duration
        ceps = cm_energy_cost / cm_duration * -1

        dps = (fdps * ceps + cdps * feps) / (ceps + feps)
        #dps = dps0 + (cdps - fdps) / (ceps + feps) * 0.5

        return f"{dps:.2f}"
    