import __init__
from core.ctx import *
from core.characterbase import *
from mod.skillupgrade import *

class Laxi(Character):
    def dconf(self):
        return {
        'acl.cancel': """
            `s1
            `s3, not this.s3_buff_on
            `s2, not this.s2on.get()
        """,
        'slot.a': 'HoH+DD',
        'slot.w': 'Agito_Tyrfing'
        }


    def conf(self):
        return {
         'star'    : 4
        ,'ele'     : 'flame'
        ,'wt'      : 'blade'
        ,'atk'     : 494
        #,'a1': Removes all buffs and debuffs on the user, grants them an HP regen buff, healing 25% Max HP every 1.5 seconds for 5 seconds, but renders them unable to move or attack for 5 seconds when HP drops to 30% (once per quest). 
        ,'a3'      : ('atk', 0.20, 'hp30') # also decreases def

        ,'s1.hit'          : [(0,'h1'),(0,'h1'),(0,'h1'),(0,'h1')]
        ,'s1.attr.h1.coef' : 0.87
        ,'s1.sp'           : 2630
        ,'s1.stop'         : 2.233
        ,'s12.hit'         : [(0,'h1'),(0,'h1'),(0,'h1'),(0,'h1'),(0,'h1'),(0,'h1'),(0,'h1'),(0,'h1')]

        ,'s2.sp'           : 4887
        ,'s2.stop'         : 1
        }

    def init(self):
        self.s2toggle = self.ToggleBuff('s2', [('self', 0.15, -1, 'atk'), None])
        self.s2on = self.s2toggle.get_buff_by_idx(0)
        self.s1upgrade = Skillupgrade(self,1,self.conf['s12'], self.s2on)

    def s2_proc(self):
        self.s2toggle()
        if self.s2toggle.c_idx == 0:
            self.s1upgrade(-1, buff_on=False)

if __name__ == '__main__':
    import run
    run.this_character()
