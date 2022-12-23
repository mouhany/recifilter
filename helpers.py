import os
import requests
import sqlite3

from flask import redirect, session
from functools import wraps
from typing import Any, List


# From CS50 pset9 Finance #######################################################


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Functions ###############################################################

def database(db="recifilter.db"):
    con = sqlite3.connect(db)
    cur = con.cursor()
    return con, cur


def lookup(param):
    try:
        api_key = os.environ.get("API_KEY")
        api_id = os.environ.get("API_ID")
        response = requests.get(
            f"https://api.edamam.com/api/recipes/v2?type=public&app_id={api_id}&app_key={api_key}&q={param}")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        result = response.json()
        # count = result["count"]
        # next = result["_links"]["next"]["href"]
        hits_dict = result["hits"]
        recipes_list = []
        for index in hits_dict:
            link = index["_links"]["self"]["href"]  # Recipe's JSON link
            label = index["recipe"]["label"]
            image = index["recipe"]["image"]
            source = index["recipe"]["source"]
            url = index["recipe"]["url"]  # Source link
            dietLabels = list(index["recipe"]["dietLabels"])
            healthLabels = list(index["recipe"]["healthLabels"])
            ingredientLines = list(index["recipe"]["ingredientLines"])
            calories = index["recipe"]["calories"]
            totalTime = index["recipe"]["totalTime"]
            cuisineType = list(index["recipe"]["cuisineType"])
            dishType = list(index["recipe"]["dishType"])
            recipes_list.append(
                {
                    "link": link,
                    "label": label,
                    "image": image,
                    "source": source,
                    "url": url,
                    "dietLabels": dietLabels,
                    "healthLabels": healthLabels,
                    "ingredientLines": ingredientLines,
                    "calories": calories,
                    "totalTime": totalTime,
                    "cuisineType": cuisineType,
                    "dishType": dishType
                })
        return recipes_list  # , next, count
    except (KeyError, TypeError, ValueError):
        return None


def readable_list(seq: List[Any]) -> str:
    """
    Grammatically correct human readable string from list (with Oxford comma)
    https://stackoverflow.com/a/53981846/19845029
    """
    seq = [str(s) for s in seq]
    if len(seq) < 3:
        return ' and '.join(seq)
    return ', '.join(seq[:-1]) + ', and ' + seq[-1]


# def lookup_recipe(link):
#     try:
#         response = requests.get(link)
#         response.raise_for_status()
#     except requests.RequestException:
#         return None
#     try:
#         result = response.json()
#         print(type(result))  # dict
#         recipe_info = []
#         for key in result:
#             link = key["_links"]["self"]["href"]
#             label = key["recipe"]["label"]
#             image = key["recipe"]["image"]
#             source = key["recipe"]["source"]
#             url = key["recipe"]["url"]
#             dietLabels = list(key["recipe"]["dietLabels"])
#             healthLabels = list(key["recipe"]["healthLabels"])
#             ingredientLines = list(key["recipe"]["ingredientLines"])
#             calories = key["recipe"]["calories"]
#             totalTime = key["recipe"]["totalTime"]
#             cuisineType = key["recipe"]["cuisineType"]
#             dishType = key["recipe"]["dishType"]
#             recipe_info.append(
#                 {
#                     "link": link,
#                     "label": label,
#                     "image": image,
#                     "source": source,
#                     "url": url,
#                     "dietLabels": dietLabels,
#                     "healthLabels": healthLabels,
#                     "ingredientLines": ingredientLines,
#                     "calories": calories,
#                     "totalTime": totalTime,
#                     "cuisineType": cuisineType,
#                     "dishType": dishType
#                 })
#         return recipe_info
#     except (KeyError, TypeError, ValueError):
#         return None
