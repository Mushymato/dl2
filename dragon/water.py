import __init__
from dragon.dragonbase import *

class Dragonyule_Jeanne(Dragon):
    ele = 'water'
    atk = 125
    a = [('atk', 0.45),
        ('cc', 0.2)]
DJ = Dragonyule_Jeanne

class Siren(Dragon):
    ele = 'water'
    atk = 125
    a = [('atk', 0.20),
        ('sd', 0.90)]


class Leviathan(Dragon):
    ele = 'water'
    atk = 125
    a = [('atk',0.60)]


class Halloween_Maritimus(Dragon):
    ele = 'water'
    atk = 119
    a = [('sp', 0.35)]
H_Mariti = Halloween_Maritimus

class Kamuy(Dragon):
    ele = 'water'
    atk = 125
    a = [('skill_link', 0.15, 'atk'), ('atk', 0.45)]