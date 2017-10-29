#!/usr/bin/python3

import yaml
import db
import sys

def yaml2db(yamldata, db, force=True):
    print(data)
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
    dbfile = "testdb.sqlite"

    data = yaml.load(open(filename, 'r'))
    db = db.CocktailDB(dbfile)
    missing_ingredients= yaml2db(data, db)
    print(ingredients2yaml(missing_ingredients))
