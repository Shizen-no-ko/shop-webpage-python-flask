from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash
from datetime import datetime
from random import shuffle

load_dotenv()
art_list = ["about.png", "boat.png", "bus.png", "elephantus.png", "gojongarr.png", "hana.png", "hula.png", "lenny.png", "leonard.png", "paradies.png", "station.png", "the_handbag.png", "this_is_the_way.png", "zowie.png"]
art_path_list = [f"static/images/art/{a}" for a in art_list]
shuffle(art_path_list)
print(art_path_list)
now = datetime.now()
current_year = now.strftime("%Y")

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def home():
	return render_template("index.html", art_list=art_path_list, current_year=current_year)


if __name__ == "__main__":
	app.run(debug=True)
