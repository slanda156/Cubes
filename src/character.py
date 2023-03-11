from pygame import Surface
from src.equipment import weapon, armor

class character:
    """Character frame"""
    ...

class player(character):
    """A playable character"""
    def __init__(self,
    pos: list[int],
    team: int,
    usedWeapon: weapon,
    usedArmor: armor,
    speed: int,
    gamesurf: Surface
    ):
        ...

    def addItem(self, item):
        ...
    
class enemy(character):
    """Enemy character"""
    ...

class characterList(list):
    def getPlayer(self) -> list[player]:
        """Return a list with all players"""
        players = []
        for p in self:
            if p.player:
                players.append(p)
        return players

    def empty(self) -> None:
        """Deletes the content of the list"""
        for i in range(len(self)-1):
            del self[i]
        return None
