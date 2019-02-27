import random

rocket = "\U0001f680"
doughnut = "\U0001f369"
cake = "\U0001f370"
pizza = "\U0001f355"
cupcake = "\U0001f9c1"
candybar = "\U0001f36b"
guitar = "\U0001f3b8"
popcorn = "\U0001f37f"


skip = "\U000026d4 "

noskip = ""


def nopositive():
    return ""


def positive():
    emojis = [rocket, doughnut, cake, pizza, cupcake, candybar, guitar, popcorn]

    return random.choice(emojis)
