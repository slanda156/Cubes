# Importing modules
import logging
import json

# Define logger
logger = logging.getLogger(__name__)

# Load damage types
with open("classes\\damageTypes.json") as f:
    damageTypes = json.load(f)

itemNum = 1

items = []

def initItem(l):
    global logger
    logger = l
    logger.info("Loading items")
    for i in range(itemNum):
        items.append(item(i))

class item:
    def __init__(self, index):
        self.name = "None"
        self.displayName = "None"
        self.amount = 1
        self.healing = 0
        self.cost = 0

        if index == 0:
            self.medKit()


    def medKit(self):
        self.name = "medKit"
        self.displayName = "Med Kit"
        self.healing = 20
        self.cost = 20
