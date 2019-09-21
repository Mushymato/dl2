import __init__
from core.ctx import *
from core.characterbase import *
from target.dummy import *
from mod.skillshift import *


class Mikoto(Character):
    def config(this, conf):
        conf.name    = 'Mikoto'
        conf.star    = 5
        conf.ele     = 'flame'
        conf.wt      = 'blade'
        conf.atk     = 520
        conf.a1      = ('cc', 0.10, 'hp70')
        conf.a3      = ('cc', 0.08)
        conf.slot.w  = 'c534_flame'
        #conf.slot.w  = 'v534_flame_zephyr'
        #conf.slot.d  = 'Cerb'
        #conf.slot.d  = 'Arctos'
        conf.slot.d  = 'Sakuya'
        conf.slot.a1 = 'RR'
        conf.slot.a2 = 'BN'

        conf.s1.recovery = 1.62  # 1.83 2.8
        conf.s1.sp = 4500
        conf.s1.hit = [
                (0.18, 'h1'), 
                (0.43, 'h1'), 
                ]
        conf.s1.attr.h1.coef = 5.32
        conf.s1.attr.h2.coef = 3.54
        conf.s1.attr.h3.coef = 2.13
        conf.s1.attr.h4.coef = 4.25

        conf.s2.recovery = 1
        conf.s2.sp = 4500
        conf.s2.buff = ('self', 0.2, 10, 'spd')

    def s1_proc(this):
        this.target.Debuff('s1',0.1)(10)


    def init(this):
        this.stance = 0
        this.conf.s1.on_end = this.s1_end

        this.conf.s12.recovery = 1.83
        this.conf.s12.hit = [(0.23,'h2'), (0.42,'h2'), (0.65,'h2')]

        this.conf.s13.recovery = 2.8
        this.conf.s13.hit = [(0.22,'h3'), (0.42,'h3'),
                             (0.65,'h3'), (1.15,'h4')]

        this.ss = Skillshift(this, 1, this.conf.s12, this.conf.s13)
        

    def s1_end(this):
        if this.stance == 0:
            this.stancebuff = this.Selfbuff('s1', 0.10)(20)
            this.stancebuff.end = this.clean_stance
            this.stance = 1
        elif this.stance == 1:
            this.stancebuff.off()
            this.stancebuff = this.Selfbuff('s1', 0.15)(15)
            this.stancebuff.end = this.clean_stance
            this.stance = 2
        else:
            this.stance = 0
            this.stancebuff.off()


    def clean_stance(this):
        this.stance = 0
        this.ss.reset()




if __name__ == '__main__':
    #logset(['buff', 'dmg', 'od', 'bk'])
    logset(['buff', 'dmg', 'bk', 'sp'])
    #logset('x')
    logset('fs')
    #logset('act')
    logset('s')
    #logset(['buff','debug','dmg', 'hit'])

    tar = Dummy()
    tar.init()

    c = Mikoto()
    c.tar(tar)
    c.init()

    Timer.run(60)
    logcat()