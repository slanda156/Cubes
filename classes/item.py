# Import modules
import json
from classes.constants import logger

class item:
    def __init__(self, name, displayName, category, uses, args):
        self.name = name
        self.displayName = displayName
        self.category = category
        self.uses = uses
        self.number = 0

        if "healing" in args:
            self.healing = args["healing"]

        if "damage" in args:
            self.healing = args["damage"]

# Loading items
logger.info("Loading items")
with open("classes\\item.json") as f:
    rawItems = json.load(f)

items = {}

for x in rawItems:
    x = rawItems[x]
    name = x.get("name")
    displayName = x.get("displayName")
    category = x.get("category")
    uses = x.get("uses")
    cost = x.get("cost")
    args = x.get("args")
    items[name] = item(name, displayName, category, uses, args)
