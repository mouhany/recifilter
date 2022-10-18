from curses.ascii import isalnum
import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import login_required, lookup, readable_list


# From CS50 Finance #######################################################


# Configure app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///recifilter.db")

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
    'balanced': 'Balanced',
    'high-fiber': 'High Fiber',
    'high-protein': 'High Protein',
    'low-carb': 'Low Carb',
    'low-fat': 'Low Fat',
    'low-sodium': 'Low Sodium'
}

healthlabels1 = {
    'alcohol-cocktail': 'Alcohol-Cocktail',
    'alcohol-free': 'Alcohol-Free',
    'celery-free': 'Celery-Free',
    'crustacean-free': 'Crustacean-Free',
    'dairy-free': 'Dairy-Free',
    'DASH': 'DASH',
    'egg-free': 'Egg-Free',
    'fish-free': 'Fish-Free',
    'fodmap-free': 'FODMAP-Free',
    'gluten-free': 'Gluten-Free',
    'immuno-supportive': 'Immuno-Supportive',
    'keto-friendly': 'Keto-Friendly',
}
healthlabels2 = {
    'kidney-friendly': 'Kidney-Friendly',
    'kosher': 'Kosher',
    'low-potassium': 'Low-Potassium',
    'low-sugar': 'Low-Sugar',
    'lupine-free': 'Lupine-Free',
    'Mediterranean': 'Mediterranean',
    'mollusk-free': 'Mollusk-Free',
    'mustard-free': 'Mustard-Free',
    'No-oil-added': 'No oil added',
    'paleo': 'Paleo',
    'peanut-free': 'Peanut-Free',
    'pescatarian': 'Pescatarian',
}
healthlabels3 = {
    'pork-free': 'Pork-Free',
    'red-meat-free': 'Red-Meat-Free',
    'sesame-free': 'Sesame-Free',
    'shellfish-free': 'Shellfish-Free',
    'soy-free': 'Soy-Free',
    'sugar-free': 'Sugar-Free',
    'sugar-conscious': 'Sugar-Conscious',
    'sulfite-free': 'Sulfite-Free',
    'tree-nut-free': 'Tree-Nut-Free',
    'vegan': 'Vegan',
    'vegetarian': 'Vegetarian',
    'wheat-free': 'Wheat-Free'
}

cuisinetype1 = {
    'american': 'American',
    'asian': 'Asian',
    'british': 'British',
    'caribbean': 'Caribbean',
    'central europe': 'Central Europe',
    'chinese': 'Chinese',
    'eastern europe': 'Eastern Europe'
}
cuisinetype2 = {
    'french': 'French',
    'greek': 'Greek',
    'indian': 'Indian',
    'italian': 'Italian',
    'japanese': 'Japanese',
    'korean': 'Korean',
    'kosher': 'Kosher',
}
cuisinetype3 = {
    'Mediterranean': 'Mediterranean',
    'mexican': 'Mexican',
    'middle eastern': 'Middle Eastern',
    'nordic': 'Nordic',
    'south american': 'South American',
    'south east asian': 'South East Asian',
    'world': 'World'
}

dishtype = {
    'starter': 'Starter',
    'main course': 'Main Course',
    'side dish': 'Side Dish',
    'drinks': 'Drinks',
    'desserts': 'Desserts'
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
    name = db.execute("SELECT name FROM users WHERE id = ?",
                      session["user_id"])
    return render_template("index.html",
                           name=name,
                           # Pass key-value pair from dictionaries to be rendered in index.html
                           dietlabels=dietlabels, healthlabels1=healthlabels1, healthlabels2=healthlabels2, healthlabels3=healthlabels3, cuisinetype1=cuisinetype1, cuisinetype2=cuisinetype2, cuisinetype3=cuisinetype3, dishtype=dishtype)


@app.route("/result")
@login_required
def result():
    # Get all input values including the empty ones
    i_list = request.args.getlist("ingredients")
    # Remove empty values with list comprehension
    ingredients_list = [i.lower().strip() for i in (filter(None, i_list))]
    dish_list = request.args.getlist("dishType")
    diet_list = request.args.getlist("dietLabels")
    health_list = request.args.getlist("healthLabels")
    cuisine_list = request.args.getlist("cuisineType")

    # Format list to comma-separated string
    ingredients = str(','.join(ingredients_list))

    # Make ingredients readable for result page's headline
    li = list(ingredients.split(','))
    listofingredients = readable_list(li)

    dish_Array = []
    for d in dish_list:
        dish_Array.append("&dishType=" + d)

    d_Array = []
    for d in diet_list:
        d_Array.append("&diet=" + d)

    h_Array = []
    for h in health_list:
        h_Array.append("&health=" + h)

    c_Array = []
    for c in cuisine_list:
        c_Array.append("&cuisineType=" + c)

    dishType = ''.join(dish_Array)
    dietLabels = ''.join(d_Array)
    healthLabels = ''.join(h_Array)
    cuisineType = ''.join(c_Array)

    # Concat all parameters
    param = ''.join(ingredients+dishType+dietLabels +
                    healthLabels+cuisineType)

    # Make API request
    recipes_list = lookup(param)

    saved_recipes_link = db.execute(
        "SELECT link FROM bookmarks WHERE user_id = ?", session["user_id"])

    return render_template("result.html",
                           # Readable list of ingredients
                           listofingredients=listofingredients,
                           # Result
                           recipes_list=recipes_list,
                           # User input tag
                           dish_list=dish_list,
                           diet_list=diet_list,
                           health_list=health_list,
                           cuisine_list=cuisine_list,
                           # Bookmark button exception
                           saved_recipes_link=saved_recipes_link,
                           # Dishtype
                           dishtype=dishtype)


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
    ingredientLines = request.form.get(
        "ingredientLines").strip("[]").strip(",")

    db.execute("INSERT INTO bookmarks (user_id, link, label, image, source, url, calories, totaltime, dishtype, dietlabels, healthlabels, cuisinetype, ingredientlines) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               session["user_id"], link, label, image, source, url, calories, totalTime, dishType, dietLabels, healthLabels, cuisineType, ingredientLines)

    return redirect("/bookmarks")


@app.route("/bookmarks")
@login_required
def bookmarks():
    saved_recipes_list = db.execute(
        "SELECT * FROM bookmarks WHERE user_id = ?", session["user_id"])

    return render_template("bookmarks.html", saved_recipes_list=saved_recipes_list, dishtype=dishtype)


@app.route("/remove", methods=["POST"])
@login_required
def remove():
    link = request.form.get("link")

    db.execute("DELETE FROM bookmarks WHERE link = (?)", link)

    return redirect("/bookmarks")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            message = "Please enter a valid username and/or password!"
            return render_template("login.html", message=message)

        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            message = "Invalid username and/or password!"
            return render_template("login.html", message=message)

        session["user_id"] = rows[0]["id"]
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
            return render_template("register.html", message=message)
        if len(username) < 4 or not username.isalnum():
            message = "Username should be a minimum of four alphanumeric (A-z, 0-9) characters!"
            return render_template("register.html", message=message)

        pw = generate_password_hash(password)

        try:
            user = db.execute(
                "INSERT INTO users (name, username, hash) VALUES (?, ?, ?)", name, username, pw)
            session["user_id"] = user
            return redirect("/")
        except:
            message = "Username has been taken. Please pick a different username!"
            return render_template("register.html", message=message)

    else:
        return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    row = db.execute(
        "SELECT * FROM users WHERE id = ?", session["user_id"])
    currentname = row[0]["name"]
    currentusername = row[0]["username"]

    if request.method == "GET":
        # Return message1 so the "Edit Name" tab is set to active when user reach route via get
        message1 = " "
        return render_template("settings.html", row=row, currentname=currentname, currentusername=currentusername, message1=message1)

    else:
        name = request.form.get("change_name").strip()
        if name:
            db.execute("UPDATE users SET name = ? WHERE id = ?",
                       name, session["user_id"])
            currentname = name
            message1 = "Name has successfully changed!"
            return render_template("settings.html", row=row, message1=message1, currentname=currentname, currentusername=currentusername)

        username = request.form.get("change_username").strip()
        if username:
            if len(username) < 4 or not username.isalnum():
                message2 = "Username should be a minimum of four alphanumeric (A-z, 0-9) characters!"
                return render_template("settings.html", row=row, message2=message2, currentname=currentname, currentusername=currentusername)
            try:
                db.execute("UPDATE users SET username = ? WHERE id = ?",
                           username, session["user_id"])
                currentusername = username
            except:
                message2 = "Username has been taken. Please pick a different username!"
                return render_template("settings.html", row=row, message2=message2, currentusername=currentusername, currentname=currentname)
            message2 = "Username has successfully changed!"
            return render_template("settings.html", row=row, message2=message2, currentusername=currentusername, currentname=currentname)

        currentpassword = request.form.get("currentpassword").strip()
        newpassword = request.form.get("newpassword").strip()
        # newpassword is hashed so it can be used to check_password_hash
        password = generate_password_hash(newpassword)
        confirmpassword = request.form.get("confirmpassword").strip()
        if currentpassword and newpassword and confirmpassword:
            if len(newpassword) < 8:
                message3 = "Password should be a minimum of eight characters!"
                return render_template("settings.html", row=row, message3=message3, currentusername=currentusername, currentname=currentname)
            # check_password_hash(pwhashed, pwplaintext)
            if not check_password_hash(row[0]["hash"], currentpassword):
                message3 = "Current password is incorrect!"
                return render_template("settings.html", row=row, message3=message3, currentusername=currentusername, currentname=currentname)
            if not check_password_hash(password, confirmpassword):
                message3 = "New password and confirmation don't match!"
                return render_template("settings.html", row=row, message3=message3, currentusername=currentusername, currentname=currentname)
            db.execute("UPDATE users SET hash = ? WHERE id = ?",
                       password, session["user_id"])
            message3 = "Password has successfully changed!"
            return render_template("settings.html", row=row, message3=message3, currentusername=currentusername, currentname=currentname)

        # If user doesn't change anything but clicked 'save changes'
        return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
