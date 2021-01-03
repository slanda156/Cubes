# Import needed modules
import pygame as py

class effect:
    def __init__(self, effectType, effectDuration, effectDamage, effectColor):
        self.type = effectType
        self.duration = effectDuration
        self.damage = effectDamage
        self.color = effectColor