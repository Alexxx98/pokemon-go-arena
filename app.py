from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from modules import Pokemon
from PIL import Image
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


def overlay_image(sprite, effect):
    effect_path = f"static/images/{effect}"

    sprite = Image.open(sprite) 
    effect = Image.open(effect_path)

    effect.resize((10, 10))
    sprite.resize((15, 15))

    sprite.paste(effect)

    return sprite


@app.route('/')
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

        fm = pokemon.get_fast_move()
        cm = pokemon.get_charge_move()
        types = pokemon.get_types()
        stats = pokemon.get_pokemon_stats()
        atk_stat = stats['base_attack']
        atk_iv = pokemon.iv[0]

        dps = pokemon.calculate_dps(fm, cm, types, atk_stat, atk_iv)
        sprite = pokemon.get_sprite(stats, name, is_shiny)

        shadow_fire = "shadow_fire.png"
        shadow_sprite = overlay_image(sprite, shadow_fire)
        shadow_sprite.save("static/images/shadowmon.png")
    else:
        dps, sprite, is_shiny, shadow_sprite = None, None, None, None

    return render_template('dps.html', dps=dps, sprite=sprite, is_shiny=is_shiny, shadow_sprite=shadow_sprite)

if __name__ == "__main__":
    app.run(debug=True, port=5002)