import __init__
from core.ctx import *
from core.characterbase import *
from mod.skillshift import *
from mod.afflic import *


class Mikoto(Character):
    def dconf(this):
        conf = {
         'slot.d'  : 'Arctos'
        ,'acl.cancel': """
            `s1, x=5
            `s2, x=5
            `s3, x=5
            `fsf, x=5
        """
        }
        #if 'wand' in this.ex:
        #    conf['slot.d'] = 'Sakuya'
        return conf


    def conf(this):
        return {
         'star'    : 5
        ,'ele'     : 'flame'
        ,'wt'      : 'blade'
        ,'atk'     : 520
        ,'a1'      : ('cc', 0.10,'hp70')
        ,'a3'      : ('cc', 0.08)

        ,'s1.stop'         : 1.4  # 1.633 2.8
        ,'s1.sp'           : 4500
        ,'s1.hit'          : [(0.18,'h1'),
                              (0.43,'h1')]
        ,'s1.attr.h1.coef' : 5.32
        ,'s1.attr.h2.coef' : 3.54
        ,'s1.attr.h3.coef' : 2.13
        ,'s1.attr.h4.coef' : 4.25

        ,'s2.stop'         : 1
        ,'s2.sp'           : 4500
        ,'s2.buff'         : ('self', 0.2, 10,'spd')
        }


    def init(this):

        this.stance = 0
        conf = {
                 's12.stop'     : 1.633
                ,'s12.hit'      : [(0.23,'h2'), (0.42,'h2'), (0.65,'h2')]
                ,'s13.stop'     : 2.8
                ,'s13.hit'      : [(0.22,'h3'), (0.42,'h3'),
                                     (0.65,'h3'), (1.15,'h4')]
                }
        this.conf_w.update(conf)

        this.ss = Skillshift(this, 1, this.conf['s12'], this.conf['s13'])
        

    def s1_end(this):
        if this.stance == 0:
            this.stancebuff = this.Selfbuff('s1', 0.10)(20)
            this.stancebuff.on_end.append(this.clean_stance)
            this.stance = 1
        elif this.stance == 1:
            this.stancebuff.on_end = []
            this.stancebuff.off()
            this.stancebuff = this.Selfbuff('s1', 0.15)(15)
            this.stancebuff.on_end.append(this.clean_stance)
            this.stance = 2
        else:
            this.stance = 0
            this.stancebuff.on_end = []
            this.stancebuff.off()

    def clean_stance(this):
        this.stance = 0
        this.ss.reset()


if __name__ == '__main__':
    import run
    run.this_character()
