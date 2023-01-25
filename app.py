import os

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from curses.ascii import isalnum

from helpers import login_required, database, split_dict, stringify, lookup, readable_list


# From CS50 pset9 Finance #######################################################

# Configure app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Make sure API_KEY and API_ID are set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")
elif not os.environ.get("API_ID"):
    raise RuntimeError("API_ID not set")


@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Dictionaries ############################################################


dietlabels = {
    "balanced": "Balanced",
    "high-fiber": "High Fiber",
    "high-protein": "High Protein",
    "low-carb": "Low Carb",
    "low-fat": "Low Fat",
    "low-sodium": "Low Sodium",
}

healthlabels = {
    "pescatarian": "Pescatarian",
    "shellfish-free": "Shellfish-Free",
    "alcohol-free": "Alcohol-Free",
    "celery-free": "Celery-Free",
    "soy-free": "Soy-Free",
    "sugar-free": "Sugar-Free",
    "pork-free": "Pork-Free",
    "red-meat-free": "Red-Meat-Free",
    "sesame-free": "Sesame-Free",
    "sulfite-free": "Sulfite-Free",
    "tree-nut-free": "Tree-Nut-Free",
    "vegan": "Vegan",
    "sugar-conscious": "Sugar-Conscious",
    "vegetarian": "Vegetarian",
    "wheat-free": "Wheat-Free",
    "alcohol-cocktail": "Alcohol-Cocktail",
    "crustacean-free": "Crustacean-Free",
    "dairy-free": "Dairy-Free",
    "lupine-free": "Lupine-Free",
    "mediterranean": "Mediterranean",
    "dash": "DASH",
    "kidney-friendly": "Kidney-Friendly",
    "egg-free": "Egg-Free",
    "fish-free": "Fish-Free",
    "fodmap-free": "FODMAP-Free",
    "gluten-free": "Gluten-Free",
    "mollusk-free": "Mollusk-Free",
    "peanut-free": "Peanut-Free",
    "immuno-supportive": "Immuno-Supportive",
    "keto-friendly": "Keto-Friendly",
    "low-sugar": "Low-Sugar",
    "mustard-free": "Mustard-Free",
    "kosher": "Kosher",
    "low-potassium": "Low-Potassium",
    "no-oil-added": "No oil added",
    "paleo": "Paleo",
}

cuisinetype = {
    "chinese": "Chinese",
    "eastern europe": "Eastern Europe",
    "british": "British",
    "caribbean": "Caribbean",
    "asian": "Asian",
    "central europe": "Central Europe",
    "american": "American",
    "french": "French",
    "kosher": "Kosher",
    "indian": "Indian",
    "korean": "Korean",
    "italian": "Italian",
    "greek": "Greek",
    "japanese": "Japanese",
    "mediterranean": "Mediterranean",
    "south east asian": "South East Asian",
    "mexican": "Mexican",
    "south american": "South American",
    "world": "World",
    "nordic": "Nordic",
    "middle eastern": "Middle Eastern",
}

dishtype = {
    "starter": "Starter",
    "main course": "Main Course",
    "side dish": "Side Dish",
    "drinks": "Drinks",
    "desserts": "Desserts",
    # 'alcohol cocktail': 'Alcohol Cocktail',
    # 'biscuits and cookies': 'Biscuit and Cookies',
    # 'bread': 'Bread',
    # 'cereals': 'Cereals',
    # 'condiments and sauces': 'Condiments and Sauces',
    # 'desserts': 'Desserts',
    # 'drinks': 'Drinks',
    # 'egg': 'Egg',
    # 'ice cream and custard': 'Ice Cream and Custard',
    # 'main course': 'Main Course',
    # 'pancake': 'Pancake',
    # 'pasta': 'Pasta',
    # 'pastry': 'Pastry',
    # 'pies and tarts': 'Pies and Tarts',
    # 'pizza': 'Pizza',
    # 'preps': 'Preps',
    # 'preserve': 'Preserve',
    # 'salad': 'Salad',
    # 'sandwiches': 'Sandwiches',
    # 'seafood': 'Seafood',
    # 'side dish': 'Side Dish',
    # 'soup': 'Soup',
    # 'special occasions': 'Special Occasions',
    # 'starter': 'Starter',
    # 'sweets': 'Sweets'
}


# Routes ##################################################################


@app.route("/")
@login_required
def index():
    con, cur = database()
    name = cur.execute("SELECT name FROM users WHERE id = ?",
        (session["user_id"],)
    )
    name = name.fetchall()
    con.close()

    hl = split_dict(healthlabels, 3)
    ct = split_dict(cuisinetype, 3)

    return render_template("index.html",
        name=name,
        dietlabels=dietlabels,
        hl=hl,
        len_hl=len(hl),
        ct=ct,
        len_ct=len(ct),
        dishtype=dishtype,
    )


@app.route("/result")
@login_required
def result():
    i_list = request.args.getlist("ingredients")
    # Remove empty values (if any) with list comprehension
    ingredients_list = [i.lower().strip() for i in (filter(None, i_list))]
    ingredients = str(",".join(ingredients_list))
    
    # Make ingredients readable for result page's headline
    readable_ingredients = readable_list(ingredients_list)

    dishType = stringify("dishType", "&dishType=")
    dietLabels = stringify("dietLabels", "&diet=")
    healthLabels = stringify("healthLabels", "&health=")
    cuisineType = stringify("cuisineType", "&cuisineType=")
    
    # Concat all parameters
    param = "".join(ingredients + dishType[1] + dietLabels[1] + healthLabels[1] + cuisineType[1])

    # Make API request
    recipes_list = lookup(param)

    con, cur = database()
    saved_recipes_link = cur.execute("SELECT link FROM bookmarks WHERE user_id = ?",
        (session["user_id"],)
    )
    saved_recipes_link = saved_recipes_link.fetchall()
    con.close()

    return render_template("result.html",
        readable_ingredients=readable_ingredients,
        recipes_list=recipes_list,
        dish_list=dishType[0],
        diet_list=dietLabels[0],
        health_list=healthLabels[0],
        cuisine_list=cuisineType[0],
        saved_recipes_link=saved_recipes_link,
        dishtype=dishtype,
    )


@app.route("/add", methods=["POST"])
@login_required
def add():
    # String
    link = request.form.get("link")
    label = request.form.get("label")
    image = request.form.get("image")
    source = request.form.get("source")
    url = request.form.get("url")
    calories = request.form.get("calories")
    totalTime = request.form.get("totalTime")

    # List
    dishType = request.form.get("dishType").strip("[]").strip(",")
    dietLabels = request.form.get("dietLabels").strip("[]").strip(",")
    healthLabels = request.form.get("healthLabels").strip("[]").strip(",")
    cuisineType = request.form.get("cuisineType").strip("[]").strip(",")
    ingredientLines = request.form.get("ingredientLines").strip("[]")

    con, cur = database()
    cur.execute("INSERT INTO bookmarks (user_id, link, label, image, source, url, calories, totaltime, dishtype, dietlabels, healthlabels, cuisinetype, ingredientlines) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (session["user_id"],
        link,
        label,
        image,
        source,
        url,
        calories,
        totalTime,
        dishType,
        dietLabels,
        healthLabels,
        cuisineType,
        ingredientLines)
    )
    con.commit()
    con.close()

    return redirect("/bookmarks")


@app.route("/bookmarks")
@login_required
def bookmarks():
    con, cur = database()
    saved_recipes_list = cur.execute("SELECT * FROM bookmarks WHERE user_id = ?",
        (session["user_id"],)
    )
    saved_recipes_list = saved_recipes_list.fetchall()
    con.close()

    return render_template("bookmarks.html",
        saved_recipes_list=saved_recipes_list,
        dishtype=dishtype,
    )


@app.route("/remove", methods=["POST"])
@login_required
def remove():
    link = request.form.get("link")

    con, cur = database()
    cur.execute("DELETE FROM bookmarks WHERE link = (?)",
        (link,)
    )
    con.commit()
    con.close()

    return redirect("/bookmarks")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            message = "Please enter a valid username and/or password!"
            return render_template("login.html", 
                message=message,
            )

        con, cur = database()
        rows = cur.execute("SELECT * FROM users WHERE username = ?",
            (request.form.get("username"),)
        )
        rows = rows.fetchall()
        
        validate_password = check_password_hash(rows[0][3], request.form.get("password"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not validate_password:
            message = "Invalid username and/or password!"
            return render_template("login.html",
                message=message,
            )

        session["user_id"] = rows[0][0]
        con.close()

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name").strip()
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not name or not username or not password:
            message = "Please enter a valid name and/or username and/or password!"
            return render_template("register.html",
                message=message,
            )
        if len(username) < 4 or not username.isalnum():
            message = "Username should be a minimum of four alphanumeric (A-z, 0-9) characters!"
            return render_template("register.html",
                message=message,
            )

        pw = generate_password_hash(password)

        try:
            con, cur = database()
            user = cur.execute("INSERT INTO users (name, username, hash) VALUES (?, ?, ?)",
                (name,
                username,
                pw)
            )
            con.commit()
            con.close()

            session["user_id"] = user

            return redirect("/")
        except:
            message = "Username has been taken. Please pick a different username!"
            return render_template("register.html",
                message=message,
            )

    else:
        return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    con, cur = database()
    row = cur.execute("SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    )
    row = row.fetchall()
    currentname = row[0][1]
    currentusername = row[0][2]

    if request.method == "GET":
        # Return message1 so the "Edit Name" tab is set to active when user reach route via get
        message1 = " "
        return render_template("settings.html",
            row=row,
            currentname=currentname,
            currentusername=currentusername,
            message1=message1,
        )
    else:
        # Edit name
        name = request.form.get("change_name").strip()
        if name:
            cur.execute("UPDATE users SET name = ? WHERE id = ?",
                (name,
                session["user_id"])
            )
            con.commit()
            currentname = name
            message1 = "Name has successfully changed!"
            return render_template("settings.html",
                row=row,
                message1=message1,
                currentname=currentname,
                currentusername=currentusername,
            )

        # Change username
        username = request.form.get("change_username").strip()
        if username:
            if len(username) < 4 or not username.isalnum():
                message2 = "Username should be a minimum of four alphanumeric (A-z, 0-9) characters!"
                return render_template("settings.html",
                    row=row,
                    message2=message2,
                    currentname=currentname,
                    currentusername=currentusername,
                )
            try:
                cur.execute("UPDATE users SET username = ? WHERE id = ?",
                    (username,
                    session["user_id"])
                )
                con.commit()
                currentusername = username
            except:
                message2 = "Username has been taken. Please pick a different username!"
                return render_template("settings.html",
                    row=row,
                    message2=message2,
                    currentusername=currentusername,
                    currentname=currentname,
                )
            message2 = "Username has successfully changed!"
            return render_template("settings.html",
                row=row,
                message2=message2,
                currentusername=currentusername,
                currentname=currentname,
            )

        # Change password
        currentpassword = request.form.get("currentpassword").strip()
        newpassword = request.form.get("newpassword").strip()
        # newpassword is hashed so it can be used to check_password_hash
        password = generate_password_hash(newpassword)
        confirmpassword = request.form.get("confirmpassword").strip()
        if currentpassword and newpassword and confirmpassword:
            if len(newpassword) < 8:
                message3 = "Password should be a minimum of eight characters!"
                return render_template("settings.html",
                    row=row,
                    message3=message3,
                    currentusername=currentusername,
                    currentname=currentname,
                )
            # Syntax: check_password_hash(pwhashed, pwplaintext)
            if not check_password_hash(row[0][3], currentpassword):
                message3 = "Current password is incorrect!"
                return render_template("settings.html",
                    row=row,
                    message3=message3,
                    currentusername=currentusername,
                    currentname=currentname,
                )
            if not check_password_hash(password, confirmpassword):
                message3 = "New password and confirmation don't match!"
                return render_template("settings.html",
                    row=row,
                    message3=message3,
                    currentusername=currentusername,
                    currentname=currentname,
                )
            cur.execute("UPDATE users SET hash = ? WHERE id = ?", 
                (password, 
                session["user_id"])
            )
            con.commit()
            message3 = "Password has successfully changed!"
            return render_template("settings.html",
                row=row,
                message3=message3,
                currentusername=currentusername,
                currentname=currentname,
            )

        # If user doesn't change anything but clicked "Save Changes"
        con.close()
        return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
