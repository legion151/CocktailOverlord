"""
Copyright (C) 2017 - The CocktailOverlord Authors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from db import CocktailDB
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from urllib.parse import quote, unquote
from robots.flipper import Flipper

app = Flask(__name__, static_folder="img")
db = CocktailDB("tmp.sqlite3")
c=db.get_available_cocktails()
robot = Flipper()

@app.route("/")
def cocktail_overview():
    return render_template('main.html',
                           state=robot.state,
                           cocktails=db.get_available_cocktails())

def search_list(ingredients):
    if len(ingredients) == 0:
        possible = db.cocktail_ingredients(db.get_available_cocktails())
    else:
        possible = db.cocktail_ingredients(db.find_cocktail_using_all_ingredients(ingredients))
    
    return render_template('search.html',
                           state=robot.state,
                           searching=sorted(ingredients),
                           possible=sorted(set(possible) - set(ingredients)),
                           cocktails=db.find_cocktail_using_all_ingredients(ingredients))

@app.template_filter('add_search_ingredient')
def add_search_ingredient(s,new):
    return set(s) | set([new])

@app.template_filter('del_search_ingredient')
def del_search_ingredient(s,new):
    return set(s) - set([new])

@app.template_filter('create_search_path')
def create_search_path(s):
    return '/'.join([quote(i) for i in s])

@app.route("/search/<path:searchpath>")
def search(searchpath):
    ingredients = set([ unquote(p) for p in searchpath.split("/") ])

    return search_list(ingredients)
    
@app.route("/search")
@app.route("/search/")
def search_start():
    return search_list([])

@app.route("/refill", methods=["GET", "POST"])
def refill():
    if request.method == 'GET':
        return render_template('refill.html',
                               state=robot.state,
                               locations=db.storage(),
                               ingredients=db.ingredients()
        )
    else:
        print(request.form)
        v = {}
        for key,value in request.form.items():
            storage, attribute = key.split('.')
            if not storage in v:
                v[storage] = { attribute: value }
            else:
                v[storage][attribute] = value
        print(v)
        for storage, contents in v.items():
            if contents['ingredient'] == '':
                db.set_storage_contents(storage, None, 0)
            else:
                db.set_storage_contents(storage, contents['ingredient'], contents['amount'])
        return render_template('refill.html',
                               state=robot.state,
                               locations=db.storage(),
                               ingredients=db.ingredients())

@app.route("/mix/<path:cid>")
def mix(cid):
    cocktail = db.get_cocktail(cid)
    if (robot.ser.isOpen() and
        not robot.busy()):
        ingredients = db.get_cocktail_ingredient_locations(cocktail.name)
        robot.mix(ingredients)
        print(ingredients)
    else:
            print("Error", robot.busy(), robot.ser.isOpen())
    return render_template('inprogress.html',
                           state=robot.state,
                           cocktail=cocktail, cid=cid,
                           pmax=robot.cmd_cnt,
                           pvalue=robot.cmd_cnt - robot.cmd_queue.qsize(),
                           progress=robot.progress())

@app.route("/mixing/<path:cid>")
def mixing(cid):
    cocktail = db.get_cocktail(cid)
    if not robot.busy():
        return render_template('main.html',
                               state=robot.state,
                               cocktails=db.get_available_cocktails())
    return render_template('inprogress.html',
                           state=robot.state,
                           cocktail=cocktail, cid=cid,
                           pmax=robot.cmd_cnt,
                           pvalue=robot.cmd_cnt - robot.cmd_queue.qsize(),
                           progress=robot.progress())

@app.route("/system", methods=["GET", "POST"])
def system():
    if request.method == 'POST':
        if request.form.get("connect"):
            robot.autoconnect()
        elif request.form.get("disconnect"):
            robot.disconnect()
        elif request.form.get("home"):
            robot.sendCmd(b"$h")
    return render_template('system.html',
                           state=robot.state,
                           connected=robot.ser.isOpen())

if __name__ == '__main__':
    app.debug=True
    app.run()
