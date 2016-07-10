from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler
import requests
import logging

telegramkey = open("telegramkey.txt", "r")
updater = Updater(telegramkey.read())
telegramkey.close()

mfile = open("mashapekey.txt", "r")
mashapekey = mfile.read()
mfile.close()

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def findcards(name):
    # Assumiamo che si autoescapi per ora...
    header = {
        "X-Mashape-Key": mashapekey
    }
    r = requests.get("https://omgvamp-hearthstone-v1.p.mashape.com/cards/search/" + name, headers=header)
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Qualcosa è andato storto.")

def generatetext(data):
    text = str()
    if data["type"] == "Hero":
        # Hero class
        if "playerClass" not in data:
            data["playerClass"] = "Neutral"
        text += "{0} Hero\n".format(data["playerClass"])
        # Name
        text += "{0}\n".format(data["name"])
        # Health
        text += "{0} health\n".format(data["health"])
    elif data["type"] == "Minion":
        # Rarity and class
        if "playerClass" not in data:
            data["playerClass"] = "Neutral"
        if "rarity" not in data:
            data["rarity"] = "Unobtainable"
        text += "{0} {1} Minion\n".format(data["rarity"], data["playerClass"])
        # Name
        text += "{0}\n".format(data["name"])
        # Tribe
        if "race" in data:
            text += "{0} Tribe\n".format(data["race"])
        # Mana cost
        text += "{0} mana cost\n".format(data["cost"])
        # Attack and health
        text += "{0} attack / {1} health\n".format(data["attack"], data["health"])
        # Text
        if "text" in data:
            text += "{0}\n".format(data["text"])
        # Flavor text
        if "lore" in data:
            text += "{0}\n".format(data["lore"])
    elif data["type"] == "Spell":
        # Rarity and class
        if "playerClass" not in data:
            data["playerClass"] = "Neutral"
        if "rarity" not in data:
            data["rarity"] = "Unobtainable"
        text += "{0} {1} Spell\n".format(data["rarity"], data["playerClass"])
        # Name
        text += "{0}\n".format(data["name"])
        # Mana cost
        if "cost" in data:
            text += "{0} mana cost\n".format(data["cost"])
        # Text
        if "text" in data:
            text += "{0}\n".format(data["text"])
        # Flavor text
        if "lore" in data:
            text += "{0}\n".format(data["lore"])
    elif data["type"] == "Enchantment":
        text += "Enchantment\n"
        # Name
        text += "{0}\n".format(data["name"])
        # Text
        if "text" in data:
            text += "{0}\n".format(data["text"])
    elif data["type"] == "Weapon":
        # Rarity and class
        if "playerClass" not in data:
            data["playerClass"] = "Neutral"
        if "rarity" not in data:
            data["rarity"] = "Unobtainable"
        text += "{0} {1} Weapon\n".format(data["rarity"], data["playerClass"])
        # Name
        text += "{0}\n".format(data["name"])
        # Mana cost
        text += "{0} mana cost\n".format(data["cost"])
        # Attack and health
        text += "{0} attack / {1} durability\n".format(data["attack"], data["durability"])
        # Text
        if "text" in data:
            text += "{0}\n".format(data["text"])
        # Flavor text
        if "lore" in data:
            text += "{0}\n".format(data["lore"])
    elif data["type"] == "Hero Power":
        # Hero class
        if "playerClass" not in data:
            data["playerClass"] = "Neutral"
        text += "{0} Hero Power\n".format(data["playerClass"])
        # Name
        text += "{0}\n".format(data["name"])
        # Mana cost
        text += "{0} mana cost\n".format(data["cost"])
        # Text
        text += "{0}\n".format(data["text"])
    # Image
    if "img" in data:
        text += "{0}\n".format(data["img"])
    return text


def cardlisttoresult(cardlist):
    result = list()
    for card in cardlist:
        try:
            data = {
                "id": card["cardId"],
                "title": card["name"],
                "thumb_url": card["img"] if ("img" in card) else None,
                "description": card["type"],
                "input_message_content": InputTextMessageContent(generatetext(card))
            }
        except Exception:
            print("Skipped card: " + repr(card))
            data = {
                "id": card["cardId"],
                "title": "ERROR: " + card["cardId"],
                "input_message_content": "ERROR: " + card["cardId"]
            }
        else:
            answer = InlineQueryResultArticle(**data)
            result.append(answer)
    return result

def oninlinequery(bot, update):
    query = update.inline_query.query.lower()
    bot.answerInlineQuery(update.inline_query.id, results=cardlisttoresult(findcards(query)))

updater.dispatcher.add_handler(InlineQueryHandler(oninlinequery))
updater.start_polling()
print("Bot started!")
updater.idle()
