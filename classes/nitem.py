# Import modules
import json
from classes.constants import logger

class item:
    def __init__(self, name, displayName, uses, cost, args):
        self.name = name
        self.displayName = displayName
        self.uses = uses
        self.cost = cost

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
    uses = x.get("uses")
    cost = x.get("cost")
    args = x.get("args")
    items[name] = item(name, displayName, uses, cost, args)
