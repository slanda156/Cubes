import pytest

from pygame import Surface, Vector2
from src.character import player
from src.equipment import weapons, armors, weapon, armor, items, item

def test_player():
    testPlayer = player((0, 0), 0, weapons.getFromName("rifle"), armors.getFromName("physicalArmor"), 10, Surface(Vector2(10,10)))
    testPlayer.addItem(items.getFromName("medkit"))

@pytest.mark.xfail
def test_playerWrongItem():
    testPlayer = player((0, 0), 0, weapons.getFromName("rifle"), armors.getFromName("physicalArmor"), 10, Surface(Vector2(10,10)))
    testPlayer.addItem(items.getFromName("blub"))
