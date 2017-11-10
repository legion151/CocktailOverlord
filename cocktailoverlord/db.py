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

import sqlite3

class RecipeEntry:
    def __init__(self, ingredient, amount):
        self.ingredient = ingredient
        self.amount = amount

class Ingredient:
    def __init__(self, name, abv):
        self.name = name
        self.abv = abv

    def __repr__(self):
        if self.abv == 0:
            return self.name
        else:
            return "{} ({:.1f}%)".format(self.name, 100*self.abv)

class Storage:
    def __init__(self, location, ingredient, amount):
        self.location = location
        self.ingredient = ingredient
        self.amount = amount
        
class Cocktail:
    def __init__(self, name, picture, recipe, cid=None):
        self.name = name
        self.picture = picture
        self.recipe = recipe
        self.id = cid

    def abv(self):
        total_volume = 0
        total_alcohol = 0

        for row in self.recipe:
            total_volume  += row[1]
            total_alcohol += row[1] * row[0].abv

        return total_alcohol / total_volume

    def pretty_print(self):
        return self.name + "\n" + "\n".join([
            "- {amount} ml of {name}".format(name=row.ingredient.name, amount=row.amount)
            for row in sorted(self.recipe, key=lambda entry: -entry.ingredient.abv)])

    def __repr__(self):
        return self.name

class CocktailDB:
    def __init__(self, dbfile):
        self.conn = sqlite3.connect(dbfile, check_same_thread=False)
        self.cur = self.conn.cursor()

    def create_db(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS cocktail   (id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
                                                                   name TEXT UNIQUE NOT NULL, 
                                                                   picture TEXT)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS ingredient (id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
                                                                   name TEXT UNIQUE NOT NULL,
                                                                   abv REAL NOT NULL)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS recipe     (cocktail   INTEGER NOT NULL REFERENCES cocktail(id)   ON DELETE CASCADE,
                                                                   ingredient INTEGER NOT NULL REFERENCES ingredient(id) ON DELETE CASCADE,
                                                                   amount     NUMERIC NOT NULL)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS storage    (location INTEGER PRIMARY KEY, ingredient INTEGER REFERENCES ingredient(id) ON DELETE SET NULL, amount REAL NOT NULL)""")
        self.cur.execute("CREATE VIEW IF NOT EXISTS available_ingredients (ingredient, amount) AS SELECT ingredient, SUM(amount) FROM storage GROUP BY ingredient")
        self.cur.execute("""CREATE VIEW IF NOT EXISTS recipe_plus_storage (cocktail, ingredient, amount, stored, enough) AS
                                 SELECT r.cocktail, r.ingredient, r.amount, ifnull(a.amount,0), ifnull(a.amount,0)>=r.amount AS enough FROM recipe AS r LEFT JOIN available_ingredients AS a ON a.ingredient=r.ingredient""")

        self.cur.execute("CREATE INDEX IF NOT EXISTS cocktail_name ON cocktail(name)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS ingredient_name ON ingredient(name)")
        self.cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS recipe_combination on recipe(cocktail, ingredient)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS recipe_cocktail on recipe(cocktail)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS recipe_ingredient on recipe(ingredient)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS storage_ingredient on storage(ingredient)")

    def delete_db(self):
        self.cur.execute("DROP TABLE IF EXISTS cocktail")
        self.cur.execute("DROP TABLE IF EXISTS ingredient")
        self.cur.execute("DROP TABLE IF EXISTS recipe")
        self.cur.execute("DROP INDEX IF EXISTS cocktail_name")
        self.cur.execute("DROP INDEX IF EXISTS ingredient_name")
        self.cur.execute("DROP INDEX IF EXISTS recipe_combination")
        self.cur.execute("DROP INDEX IF EXISTS recipe_cocktail")
        self.cur.execute("DROP INDEX IF EXISTS recipe_ingredient")
        self.cur.execute("DROP INDEX IF EXISTS storage_ingredient")
        self.cur.execute("DROP VIEW IF EXISTS available_ingredients")
        
    # Adds a new cocktail and returns its id
    # Setting force to True will overwrite the existing cocktail instead
    # returns id or None
    def add_cocktail(self, name, picture, ingredients, force=False):
        self.cur.execute("SELECT id FROM cocktail WHERE name=?", (name,))
        existing_id = self.cur.fetchone()
        if existing_id is not None :
            existing_id = existing_id[0]
            if not force:
                return None
            self.cur.execute("UPDATE cocktail SET picture=?", (picture,))
            self.cur.execute("DELETE FROM recipe WHERE cocktail=?", existing_id)
        else:
            self.cur.execute("INSERT INTO cocktail (name, picture) VALUES (?, ?)", (name, picture))
            existing_id = self.cur.lastrowid
            
        self.cur.executemany("INSERT INTO recipe (cocktail, ingredient, amount) SELECT :cocktail, ingredient.id, :amount FROM ingredient WHERE name=:ingredient",
                             [ {'cocktail': existing_id, 'ingredient': ingredient, 'amount': ingredients[ingredient]} for ingredient in ingredients])
        self.conn.commit()

    # Deletes a cocktail by name
    def delete_cocktail(self, name):
        self.cur.execute("DELETE FROM cocktail WHERE name=?", (name,))
        self.conn.commit()

    # Deletes a cocktail by id
    def delete_cocktail_id(self, cid):
        self.cur.execute("DELETE FROM cocktail WHERE id=?", (cid,))
        self.conn.commit()

    # Adds a new ingredients and returns its id (or false if it already existed)
    # Setting force to True will overwrite the existing ingredient instead
    def add_ingredient(self, name, abv, force=False):
        self.cur.execute("SELECT id FROM ingredient WHERE name=?", (name,))
        existing_id = self.cur.fetchone()
        if existing_id is not None:
            existing_id = existing_id[0]
            if not force:
                return None
            self.cur.execute("UPDATE ingredient SET abv=? WHERE id=?", (abv, existing_id))
            self.conn.commit()
            return existing_id
        else:
            self.cur.execute("INSERT INTO INGREDIENT (name, abv) VALUES (?, ?)", (name, abv))
            self.conn.commit()
            return self.cur.lastrowid

    # Deletes an ingredient by name, and cocktails that use it
    def delete_ingredient(self, name):
        self.cur.execute("DELETE FROM ingredient WHERE name=?", (name,))
        self.conn.commit()

    # Deletes an ingredient by id, and cocktails that use it
    def delete_ingredient_id(self, iid):
        self.cur.execute("DELETE FROM ingredient WHERE id=?", (iid,))
        self.conn.commit()

    # Sets a storage location's ingredient and amount
    def set_storage_contents(self, location, ingredient, amount = 0):
        if ingredient is None:
            self.cur.execute("INSERT OR REPLACE INTO storage (location, ingredient, amount) VALUES (:location, NULL, :amount)", {'location':location, 'amount':amount})
        else:
            self.cur.execute("INSERT OR REPLACE INTO storage (location, ingredient, amount) SELECT :location, id, :amount FROM ingredient WHERE name=:name", {'location':location, 'name':ingredient, 'amount':amount})
        self.conn.commit()

    # Sets a storage location's amount
    def set_storage_amount(self, location, amount):
        self.cur.execute("UPDATE storage SET amount=? WHERE location=?", (amount, location))
        self.conn.commit()

    def create_storage(self, positions):
        for i in range(positions):
            self.cur.execute("SELECT * FROM storage WHERE location=?", (i,))
            if self.cur.fetchone():
                continue
            self.set_storage_contents(i, None)

    def get_cocktail(self, cid):
        self.cur.execute("SELECT name, picture FROM cocktail WHERE id=?", (cid,))
        row = self.cur.fetchone()
        if not row:
            return None

        cocktail = Cocktail(row[0], row[1], {}, cid)
        self.cur.execute("SELECT i.name, i.abv, amount FROM recipe JOIN ingredient AS i ON i.id = ingredient WHERE recipe.cocktail = ?", (cid,))
        cocktail.recipe = [ RecipeEntry(Ingredient(i[0], i[1]), i[2]) for i in self.cur.fetchall() ]
        return cocktail

    # Returns all cocktails
    def get_all_cocktails(self):
        return self.matching_cocktails("SELECT id FROM cocktail ORDER BY name")
        
    # Returns cocktails for all cocktails with enough ingredients in storage
    def get_available_cocktails(self):
        return self.matching_cocktails("SELECT id FROM cocktail WHERE 0=(SELECT SUM(rps.enough)-COUNT(rps.ingredient) FROM recipe_plus_storage AS rps WHERE rps.cocktail=cocktail.id)")
    
    # Returns total amount, summing over all valid locations
    def get_ingredient_amount(self, ingredient_id):
        pass

    # Returns storage locations and total amounts needed for all ingredients of a cocktail
    def get_cocktail_ingredient_locations(self, cocktail):
        cid = self.cur.execute("SELECT id FROM cocktail WHERE name=?", (cocktail,)).fetchone()[0]
        ingredients = self.cur.execute("SELECT ingredient, amount FROM recipe WHERE cocktail=?", (cid,)).fetchall()
        return [
            (i[1], self.cur.execute("SELECT location, amount FROM storage WHERE ingredient=?", (i[0],)).fetchall())
            for i in ingredients
            ]

    # Remove the specified amount for each entry of the (storage, amount)-list
    def use_ingredients(self, storage_list):
        for row in storage_list:
            self.cur.execute("UPDATE storage SET amount=amount-? WHERE location=?", (row[1], row[0]))
        self.conn.commit()

    def find_cocktail_using_all_ingredients(self, ings, available_only=True):
        ing_ids = [ self.cur.execute("SELECT id FROM ingredient WHERE name=?", (i,)).fetchone()[0] for i in ings ]
        params = [len(ing_ids)] + ing_ids
        query = "SELECT id FROM cocktail AS c WHERE ?=(SELECT COUNT(ingredient) FROM recipe WHERE cocktail=c.id AND ingredient IN (" + ",".join(["?"]*len(ing_ids)) + "))"

        if available_only:
            query = query + " AND 0=(SELECT SUM(rps.enough)-COUNT(rps.ingredient) FROM recipe_plus_storage AS rps WHERE rps.cocktail=c.id)"
            
        return self.matching_cocktails(query, params)
    
    def find_cocktail_using_any_ingredients(self, ings, available_only=True):
        ing_ids = [self.cur.execute("SELECT id FROM ingredient WHERE name=?", (i,)).fetchone()[0] for i in ings ]
        query = "SELECT id FROM cocktail AS c WHERE 1<=(SELECT COUNT(ingredient) FROM recipe WHERE cocktail=c.id AND ingredient IN (" + ",".join(["?"]*len(ing_ids)) + "))"

        if available_only:
            query = query +" AND 0=(SELECT SUM(rps.enough)-COUNT(rps.ingredient) FROM recipe_plus_storage AS rps WHERE rps.cocktail=c.id)"
            
        return self.matching_cocktails(query, ing_ids)
        
    # Returns all cocktails matching a query that returns id as its first column
    def matching_cocktails(self, *args):
        self.cur.execute(*args)
        return [self.get_cocktail(row[0]) for row in self.cur.fetchall()]

    # Returns the set of ingredients of the listed cocktails
    def cocktail_ingredients(self, cocktails):
        ret = set()
        for c in cocktails:
            for row in c.recipe:
                ret.add(row.ingredient.name)
        return ret

    # Returns the contents of all storage locations
    def storage(self):
        self.cur.execute("SELECT location, ingredient.name, ingredient.abv, amount FROM storage LEFT JOIN ingredient ON ingredient.id = storage.ingredient ORDER BY location")
        return [ Storage(row[0], None if not row[1] else Ingredient(row[1], row[2]), row[3]) for row in self.cur.fetchall() ]
            
    def ingredients(self):
        self.cur.execute("SELECT name, abv FROM ingredient ORDER BY name");
        return [ Ingredient(row[0], row[1]) for row in self.cur.fetchall() ]
    
if __name__ == "__main__":
    db = CocktailDB("tmp.sqlite3")
    db.delete_db()
    db.create_db()
    db.add_ingredient("whisky", 0.4)
    db.add_ingredient("simple syrup", 0)
    db.add_ingredient("lime juice", 0)
    db.add_ingredient("egg white", 0)
    db.add_cocktail("Whisky Sour", None, { 'whisky': 40, 'lime juice': 20, 'simple syrup': 10 })
    db.add_cocktail("Whisky with egg white", None, { 'whisky': 40, 'egg white': 20 })
    db.set_storage_contents(0, 'whisky', 100)
    db.set_storage_contents(1, 'simple syrup', 100)
    db.set_storage_contents(2, 'lime juice', 100)
    db.set_storage_contents(3, 'lime juice', 500)
    for i in range(4, 15):
        db.set_storage_contents(i, None, 0)

    print("All cocktails:")
    print("\n\n".join([c.pretty_print() for c in db.get_all_cocktails()]))

    print("\nCocktails we can make:")
    print(db.get_available_cocktails())

    print("\nCocktails with lime juice and whisky:")
    print(db.find_cocktail_using_all_ingredients(['whisky','lime juice']))

    print("\nCocktails with egg white:")
    print(db.find_cocktail_using_all_ingredients(['egg white']))
    
    print("\nCocktails with egg white or simple syrup:")
    print(db.find_cocktail_using_any_ingredients(['egg white','simple syrup']))
