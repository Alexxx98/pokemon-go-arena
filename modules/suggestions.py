import requests


def get_name_suggestions():
    url = "https://pogoapi.net/api/v1/pokemon_stats.json"
    mega_url = "https://pogoapi.net/api/v1/mega_pokemon.json"
    response = requests.get(url)
    mega_response = requests.get(mega_url)
    if response.ok and mega_response.ok:
        data = response.json()
        mega_data = mega_response.json()
        suggestions = [
            (" ").join([pokemon["pokemon_name"], pokemon["form"]])
            for pokemon in data
            if "20" not in pokemon["form"]
        ]
        suggestions = [suggestion.replace("Normal", "") for suggestion in suggestions]
        mega_suggestions = [pokemon["mega_name"] for pokemon in mega_data]
        suggestions.extend(mega_suggestions)
    return suggestions


def get_move_suggestions(name, type):
    url = "https://pogoapi.net/api/v1/current_pokemon_moves.json"
    mega_url = "https://pogoapi.net/api/v1/mega_pokemon.json"
    response = requests.get(url)
    mega_response = requests.get(mega_url)
    if response.ok and mega_response.ok:
        data = response.json()
        mega_data = mega_response.json()

        # if pokemon is mega, consider it's regular name
        for pokemon in mega_data:
            if pokemon["mega_name"] == name:
                name = pokemon["pokemon_name"]

        suggestions = [
            (pokemon[f"{type}_moves"] + pokemon[f"elite_{type}_moves"])
            for pokemon in data
            if pokemon["pokemon_name"] == name
        ]
    return suggestions[0]
