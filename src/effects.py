from dataclasses import dataclass

@dataclass
class damageType:
    type: int = 0
    name: str = "physical"

class effect:
    def __init__(self, type, modifier):
        self.type = type
        self.modifier = modifier
        self.name = ""
        self.damage = 0
        self.duration = 0
