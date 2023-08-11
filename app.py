from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from modules import Pokemon
from modules import suggestions as sg
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# List for pokemon instances
pokemons = list()

types_colours = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
}


@app.route("/")
def index():
    return redirect("home", code=302)


@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/dps", methods=["POST", "GET"])
def dps():
    if request.method == "GET":
        suggestions = sg.get_name_suggestions()
        return render_template("dps.html", suggestions=suggestions)

    if request.method == "POST":
        name = request.form.get("name").strip()
        return redirect(url_for("pokemon_dps", name=name))


@app.route("/dps_<name>", methods=["POST", "GET"])
def pokemon_dps(name):
    fm_suggestions = sg.get_move_suggestions(name, type="fast")
    cm_suggestions = sg.get_move_suggestions(name, type="charged")
    
    if request.method == "GET":
        return render_template(
            "pokemon_dps.html",
            name=name,
            fm_suggestions=fm_suggestions,
            cm_suggestions=cm_suggestions,
        )

    if request.method == "POST":
        lvl = request.form.get("lvl")
        fast_move = request.form.get("fast_move")
        charged_move = request.form.get("charged_move")
        iv = request.form.get("iv")
        is_shadow = request.form.get("is_shadow")
        is_shiny = request.form.get("is_shiny")

        pokemon = Pokemon(name, lvl, fast_move, charged_move, iv, is_shadow)

        if name:
            pokemons.append(pokemon)

        fm = pokemon.get_fast_move()
        cm = pokemon.get_charge_move()

        if pokemon.is_mega():
            stats = pokemon.get_mega_pokemon_stats()
            atk_stat = stats["stats"]["base_attack"]
            pokemon.get_mega_types()
        else:
            stats = pokemon.get_pokemon_stats()
            atk_stat = stats["base_attack"]
            pokemon.get_types()

        atk_iv = pokemon.iv[0]

        pokemon.calculate_dps(fm, cm, atk_stat, atk_iv)

        pokemon.get_sprite(stats, name, is_shiny)
    else:
        is_shiny = None
    return render_template(
        "pokemon_dps.html",
        is_shiny=is_shiny,
        pokemons=pokemons,
        types_colours=types_colours,
        name=name,
    )


@app.route("/clear")
def clear():
    pokemons.clear()
    return redirect("dps", code=302)


@app.route("/clear_home")
def clear_home():
    pokemons.clear()
    return redirect("home", code=302)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
