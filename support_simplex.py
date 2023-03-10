import pulp
from bs4 import BeautifulSoup
import requests
from food_lists import *
import warnings
import pandas as pd
from lxml import html

def call_stored_foods(vegan, num_items, random=False):
    if vegan:
        return foods_vegan
    if random:
        warnings.warn("script is running in random mode")
        radom_list = load_random_list(num_items)
        print(f"the random list comprises: \n{radom_list}")
        return radom_list
    else:
        return choosen_foods

def calculation(foods, man):
    # Create a LP Maximize problem
    lp_prob = pulp.LpProblem('Nutrition Problem', pulp.LpMaximize)
    # Create variables for the amount of each food to eat
    food_vars = {f: pulp.LpVariable(f.replace(" ", "_") + "_amount", lowBound=0, cat='Continuous') for f in foods}
    # Set objective function: Maximize protein
    lp_prob += sum(foods[f].get("protein", 0) * food_vars[f] for f in foods)
    # Constraints for healthy intake for a grown man:
    # - at least 56 grams of protein
    if any(foods[f].get("protein") for f in foods):
        lp_prob += sum(foods[f]["protein"] * food_vars[f] for f in foods) >= 56 if man else 30
    # - at most 30% of calories from fat
    if any(foods[f].get("fat") and foods[f].get("calories") for f in foods):
        lp_prob += sum(foods[f]["fat"] * food_vars[f] for f in foods) <= 0.3 * sum(foods[f]["calories"] * food_vars[f] for f in foods)
    # - at most 300 mg of cholesterol
    if any(foods[f].get("cholesterol") for f in foods):
        lp_prob += sum(foods[f]["cholesterol"] * food_vars[f] for f in foods) <= 300 if man else 200
    # - at most 2,300 mg of sodium
    if any(foods[f].get("sodium") for f in foods):
        lp_prob += sum(foods[f]["sodium"] * food_vars[f] for f in foods) <= 2300 if man else 2000
    # - at least 20 grams of fiber
    if any(foods[f].get("fiber") for f in foods):
        lp_prob += sum(foods[f]["fiber"] * food_vars[f] for f in foods) >= 20 if man else 15
    # - at most 25 grams of sugar
    if any(foods[f].get("sugars") for f in foods):
        lp_prob += sum(foods[f]["sugars"] * food_vars[f] for f in foods) <= 25 if man else 10
    # - at least 1000 mg of calcium
    if any(foods[f].get("calcium") for f in foods):
        lp_prob += sum(foods[f]["calcium"] * food_vars[f] for f in foods) >= 1000 if man else 700
    if any(foods[f].get("iron") for f in foods):
        lp_prob += sum(foods[f]["iron"] * food_vars[f] for f in foods) >= 8 if man else 6
    if any(foods[f].get("calories") for f in foods):
        lp_prob += sum(foods[f]["calories"] * food_vars[f] for f in foods) >= 2800 if man else 1800
    if any(foods[f].get("calories") for f in foods):
        lp_prob += sum(foods[f]["calories"] * food_vars[f] for f in foods) <= 3500 if man else 2000
    # Solve the optimization problem
    status = lp_prob.solve()

    print(f'Status: {pulp.LpStatus[status]}')
    to_consume = {}
    for f in foods:
        #print(f'{f} = {food_vars[f].value()}')
        to_consume[f"{f}"] = f"{food_vars[f].value()}'"

    return to_consume

def print_case(optimal_diet):
    for key, val in optimal_diet.items():
        if int(val) > 0:
            print(f"it would be healthy to consume {int(val)} of {key} in your case")