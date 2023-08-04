from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
from modules import Pokemon
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# List for pokemon instances
pokemons = list()

types_colours = {
	'normal': '#A8A77A',
	'fire': '#EE8130',
	'water': '#6390F0',
	'electric': '#F7D02C',
	'grass': '#7AC74C',
	'ice': '#96D9D6',
	'fighting': '#C22E28',
	'poison': '#A33EA1',
	'ground': '#E2BF65',
	'flying': '#A98FF3',
	'psychic': '#F95587',
	'bug': '#A6B91A',
	'rock': '#B6A136',
	'ghost': '#735797',
	'dragon': '#6F35FC',
	'dark': '#705746',
	'steel': '#B7B7CE',
	'fairy': '#D685AD',
}


@app.route('/')
def index():
    return redirect('home', code=302)


@app.route('/home')
def home():
    return render_template('index.html')


@app.route("/dps", methods=['POST', 'GET'])
def dps():

    if request.method == 'POST':
        name = request.form.get('name')
        lvl = request.form.get('lvl')
        fast_move = request.form.get('fast_move')
        charged_move = request.form.get('charged_move')
        iv = request.form.get('iv')
        is_shadow = request.form.get('is_shadow')
        is_shiny = request.form.get('is_shiny')

        pokemon = Pokemon(name, lvl, fast_move, charged_move, iv, is_shadow)
        if name:
            pokemons.append(pokemon)

        fm = pokemon.get_fast_move()
        cm = pokemon.get_charge_move()
        pokemon.get_types()
        stats = pokemon.get_pokemon_stats()
        atk_stat = stats['base_attack']
        atk_iv = pokemon.iv[0]

        pokemon.calculate_dps(fm, cm, atk_stat, atk_iv)
        
        pokemon.get_sprite(stats, name, is_shiny)
    else:
        is_shiny = None
    return render_template('dps.html', is_shiny=is_shiny, pokemons=pokemons, types_colours=types_colours)


@app.route('/clear')
def clear():
    pokemons.clear()
    return redirect('dps', code=302)


@app.route('/clear_home')
def clear_home():
    pokemons.clear()
    return redirect('home', code=302)

if __name__ == "__main__":
    app.run(debug=True, port=5002)