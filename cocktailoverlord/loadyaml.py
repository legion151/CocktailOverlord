#!/usr/bin/python3

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

import yaml
import db
import sys

def yaml2db(yamldata, db, force=True):
    for name, percentage in data['ingredients'].items():
        db.add_ingredient(name, percentage, force)
    ingredients = set()
    for ings in data["cocktails"].values():
        ingredients.update(ings)
    missing = []
    for name in ingredients:
        if db.add_ingredient(name, 0., False):
            missing.append(name)
    for name, ingredients in data["cocktails"].items():
        db.add_cocktail(name, None, ingredients)

    return missing

def ingredients2yaml(ingredients):
    return ''.join((" %s: 0.\n" % name for name in sorted(ingredients)))

if __name__ == "__main__":
    filename = "mycocktails.yaml"
    dbfile = "tmp.sqlite3"

    data = yaml.load(open(filename, 'r'))
    db = db.CocktailDB(dbfile)
    db.create_db()
    missing_ingredients = yaml2db(data, db)
    print(ingredients2yaml(missing_ingredients))
