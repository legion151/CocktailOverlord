from db import CocktailDB
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from urllib.parse import quote

app = Flask(__name__)
db = CocktailDB("tmp.sqlite3")
c=db.get_available_cocktails()

@app.route("/")
def cocktail_overview():
    return render_template('main.html',
                           cocktails=db.get_available_cocktails())

if __name__ == '__main__':
    app.debug=True
    app.run()
