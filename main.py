from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash
from datetime import datetime

load_dotenv()

now = datetime.now()
current_year = now.strftime("%Y")

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def home():
	return render_template("index.html", current_year=current_year)


if __name__ == "__main__":
	app.run(debug=True)
