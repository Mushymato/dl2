import __init__
from dragon.dragonbase import *

class Cupid(Dragon):
    ele = 'light'
    atk = 119
    a = [('atk',0.60)]


class Takemikazuchi(Dragon):
    ele = 'light'
    atk = 124
    a = [('od', 0.25), ('atk', 0.4)]


class Corsaint_Phoenix(Dragon):
    ele = 'light'
    atk = 124
    a = [('k', 0.2, 'paralysis'), ('atk', 0.5)]


class Daikokuten(Dragon):
    ele = 'light'
    atk = 124
    a = [('atk', 0.25, 'hit15'), ('atk', 0.55)]
