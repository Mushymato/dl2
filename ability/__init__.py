if __package__ is None or __package__ == '':
    import os
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ability.abilitybase import *

from ability.all import *
from ability.basic import *
