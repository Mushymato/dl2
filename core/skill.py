import __init__
from core.ctx import *
from core.buff import *
from core.action import *


class Skill(object):
    def __init__(this, host):
        this.host = host
        this.s_prev = ''
        this.first_x_after_s = 0
        this.silence = 0
        this.silence_duration = 2 # 2s ui hide
        this.t_silence_end = Timer(this.silence_end)
        this.e_silence_end = Event('silence_end')
        this.log = Logger('s')


    def __call__(this, *args, **kwargs):
        r = _Skill(*args, **kwargs)
        r._static = this
        return r


    def silence_end(this, t):
        if this.log:
            this.log(this.host.name+', silence','end')
        this.silence = 0
        this.e_silence_end()


    def silence_start(this):
        this.silence = 1
        this.t_silence_end(this.silence_duration)


class Sp(object):
    def __init__(this, sp_max):
        this.cur = 0
        this.max = sp_max


class Conf_skl(Config):
    def default(this, conf):
        conf.type     = 's'
        conf.sp       = -1
        conf.startup  = 0.1 # ui lag
        conf.recovery = 2
        conf.on_start = None
        conf.on_end   = None
        conf.proc     = None
        conf.hit      = []
        conf.attr     = {}


    def sync(this, c):
        this.sp.max   = c.sp
        this.hit      = c.hit
        this.attr     = c.attr
        this.proc     = c.proc
        this.startup  = c.startup
        this.before   = c.before
        this.on_start = c.on_start
        
        this.init()


class _Skill(object):
    def __init__(this, name, host, conf=None):
        this.name = name
        this.host = host
        this.sp = Sp(0)
        this.firsthit = 1
        this.hit_prev = -1
        this.hit_next = 0
        this.hit_count = 0

        this.conf = Conf_skl(this, conf)

        this.ac = host.Action(this.name, this.conf)

        this.log = Logger('s')
        this.src = host.name+', '
        this.speed = host.speed # function


    def __call__(this):
        return this.tap()


    def init(this):
        this.hit_count = len(this.hit)
        this.dmg = {}
        for i in this.attr:
            label = this.attr[i]
            if i[0] == '_':
                label.name = this.name + i
            else:
                label.name = this.name
            label.proc = this.collid
            this.dmg[i] = this.host.Dmg(label)
        return this


    def charge(this, sp):
        if this.sp.max > 0:
            this.sp.cur += sp   
        #if this.charged > this.sp:  # should be 
            #this.charged = this.sp


    def check(this):
        if this.sp.max <= 0:
            if this.log:
                this.log(this.src+this.name, 'failed','no skill')
            return 0
        elif this._static.silence == 1:
            if this.log:
                this.log(this.src+this.name, 'failed','silence')
            return 0
        elif this.sp.cur < this.sp.max:
            if this.log:
                this.log(this.src+this.name, 'failed','no sp')
            return 0
        else :
            return 1


    def tap(this):
        if this.log:
            this.log(this.src+this.name, 'tap')
        if not this.check():
            return 0
        else:
            if this.log:
                this.log(this.src+this.name, 'cast')
            if this.ac():
                this.active()
                return 1
            else:
                return 0


    def buff(this, t):
        if type(this.conf.buff) == tuple:
            buffarg = this.conf.buff
            this.onebuff(buffarg)
        elif type(this.conf.buff) == list:
            for i in this.conf.buff:
                this.onebuff(i)


    def onebuff(this, buffarg):
        wide = buffarg[0]
        value = buffarg[1]
        time = buffarg[2]
        buffarg = buffarg[3:]
        if wide == 'team':
            this.host.Teambuff(this.name, value, *buffarg)(time)
        elif wide == 'self':
            this.host.Selfbuff(this.name, value, *buffarg)(time)
        elif wide == 'debuff':
            print('cant proc debuff at skill start')
            errrrrrrrrrr()
     #       this.host.target.Debuff(this.name, value, *buffarg)(time)
        elif wide == 'zone':
            this.host.Zonebuff(this.name, value, *buffarg)(time)
        else:
            this.host.Buff(this.name, value, *buffarg)(time)


    def _do(this, t):
        if this.ac.status != 1:
            return

        hitlabel = this.hit[this.hit_next][1]
        this.dmg[hitlabel]()

        this.hit_prev = this.hit_next
        this.hit_next += 1

        if this.hit_next < this.hit_count :
            timing = this.hit[this.hit_next][0] - this.hit[this.hit_prev][0]
            timing /= this.speed()
            Timer(this._do)(timing)


    def collid(this):
        if this.firsthit:
            this.firsthit = 0
            if 'debuff' in this.conf:
                buffarg = this.conf.debuff
                wide = buffarg[0]
                value = buffarg[1]
                time = buffarg[2]
                buffarg = buffarg[3:]
                this.host.target.Debuff(this.name, value, *buffarg)(time)
            if this.proc:
                this.proc()


    def active(this):
        this.firsthit = 1
        this.hit_prev = -1
        this.hit_next = 0
        Timer(this._active)(this.startup)


    def _active(this, t):
        if this.ac.status != 1:
            return

        if this.log:
            this.log('%s, %s'%(this.host.name, this.name),'cutin')

        this.sp.cur = 0
        this._static.s_prev = this.name
        # Even if animation is shorter than 2s
        # you can't cast next skill before 2s, after which ui shows
        this._static.silence_start()

        if this.on_start :
            this.on_start()

        if this.hit_next < this.hit_count :
            timing = this.hit[this.hit_next][0] / this.speed()
            Timer(this._do)(timing)

        if 'buff' in this.conf:
            timing = 0.15/this.speed()
            Timer(this.buff)(timing)


class Combo(object):
    def __init__(this, host):
        this.host = host
        this.x_prev = ''


    def __call__(this, *args, **kwargs):
        r = _Combo(*args, **kwargs)
        r._static = this
        return r


class Conf_cmb(Config):
    def default(this, conf):
        conf.type      = 'x'
        conf.idx       = 1 # 1~5
        conf.sp        = 0
        conf.startup   = 0
        conf.recovery  = 2
       #conf.on_start  = None
       #conf.on_end    = None
        conf.proc      = None
        conf.hit       = []
        conf.attr      = {}
        conf.cancel_by = ['s','fs','dodge']


    def sync(this, c):
        this.type    = c.type
        this.idx     = c.idx
        this.sp      = c.sp
        this.hit     = c.hit
        this.attr    = c.attr
        this.proc    = c.proc
        
        this.init()


class _Combo(object):
    def __init__(this, name, host, conf=None):
        this.name = name
        this.host = host
        this.sp = 0
        this.firsthit = 1
        this.hit_count = 0
        this.hit_prev= -1
        this.hit_next = 0
        this.e_x = Event('cancel')

        this.conf = Conf_cmb(this, conf)

        this.ac = host.Action(this.name, this.conf)

        this.log = Logger('x')
        this.src = this.host.name+', '
        this.speed = host.speed # function
        this.charge = host.charge


    def __call__(this):
        return this.tap()


    def init(this):
        this.hit_count = len(this.hit)
        this.dmg = {}
        for i in this.attr:
            label = this.attr[i]
            label.name = this.name
            label.proc = this.collid
            label.type = 'x'
            this.dmg[i] = this.host.Dmg(label)
        this.e_x.name = this.name
        this.e_x.type = this.type
        this.e_x.idx = this.idx
        this.e_x.last = this.hit_count
        return this


    def tap(this):
        if this.log:
            this.log(this.src+this.name, 'tap')

        if this.ac():
            this.active()
            this._static.x_prev = this.name
            return 1
        else:
            return 0


    def _do(this, t):
        if this.ac.status != 1:
            return


        hitlabel = this.hit[this.hit_next][1]
        this.dmg[hitlabel]()

        this.hit_prev = this.hit_next
        this.hit_next += 1

        if this.hit_next < this.hit_count :
            timing = this.hit[this.hit_next][0] - this.hit[this.hit_prev][0]
            timing /= this.speed()
            Timer(this._do)(timing)

        this.e_x.hit = this.hit_next
        this.e_x()


    def collid(this):
        if this.firsthit:
            this.firsthit = 0
            this.charge('x', this.sp)
            if this.proc:
                this.proc()


    def active(this):
        if this.hit_count :
            this.firsthit = 1
            this.hit_prev= -1
            this.hit_next = 0
            timing = this.hit[this.hit_next][0] / this.speed()
            Timer(this._do)(timing)


class Fs(object):
    def __init__(this, host):
        this.host = host

    def __call__(this, *args, **kwargs):
        r = _Fs(*args, **kwargs)
        r._static = this
        return r


class Conf_fs(Config):
    def default(this, conf):
        conf.type      = 'fs'
        conf.sp        = 0
        conf.startup   = 0 # charge time, which didn't affect by speed
        conf.recovery  = 2
       #conf.on_start  = None
       #conf.on_end    = None
        conf.proc      = None
        conf.hit       = []
        conf.attr      = {}
        conf.cancel_by = ['s','dodge']


    def sync(this, c):
        this.type    = c.type
        this.sp      = c.sp
        this.hit     = c.hit
        this.attr    = c.attr
        this.proc    = c.proc
        this.startup = c.startup
        
        this.init()


class _Fs(object):
    def __init__(this, name, host, conf=None):
        this.name = name
        this.host = host
        this.sp = 0
        this.firsthit = 1
        this.hit_count = 1
        this.hit_next = 0
        this.e_fs = Event('cancel')

        this.conf = Conf_fs(this, conf)

        this.ac = host.Action(this.name, this.conf)

        this.log = Logger('fs')
        this.src = host.name+', '
        this.speed = host.speed
        this.charge = host.charge


    def __call__(this):
        return this.hold()


    def init(this):
        this.hit_count = len(this.hit)
        this.dmg = {}
        for i in this.attr:
            label = this.attr[i]
            label.name = this.name
            label.proc = this.collid
            label.type = 'fs'
            this.dmg[i] = this.host.Dmg(label)
        this.e_fs.type = this.type
        this.e_fs.name = this.name
        this.e_fs.idx = 0
        this.e_fs.last = this.hit_count
        this.t_startup = Timer(this._active)
        return this


    def hold(this):
        if this.log:
            this.log(this.src+this.name, 'hold')
        if this.ac():
            this.active()
            return 1
        else:
            return 0


    def _do(this, t):
        if this.ac.status != 1:
            return

        hitlabel = this.hit[this.hit_next][1]
        this.dmg[hitlabel]()

        this.hit_prev = this.hit_next
        this.hit_next += 1

        if this.hit_next < this.hit_count :
            timing = this.hit[this.hit_next][0] - this.hit[this.hit_prev][0]
            timing /= this.speed()
            Timer(this._do)(timing)

        this.e_fs.hit = this.hit_next
        this.e_fs()


    def collid(this):
        if this.firsthit:
            this.firsthit = 0
            this.charge('fs', this.sp)
            if this.proc:
                this.proc()


    def active(this):
        if this.startup:
            this.t_startup(this.startup)
        else:
            this._active(0)


    def _active(this, t):
        if this.ac.status != 1:
            return

        if this.log:
            this.log('%s, %s'%(this.host.name, this.name),'release')

        if this.hit_count :
            this.firsthit = 1
            this.hit_next = 0
            this.hit_prev = -1
            timing = this.hit[this.hit_next][0] / this.speed()
            Timer(this._do)(timing)


class Dodge(object):
    def __init__(this, host):
        this.host = host
        this.x_prev = ''


    def __call__(this, *args, **kwargs):
        r = _Dodge(*args, **kwargs)
        r._static = this
        return r


class Conf_dodge(Config):
    def default(this, conf):
        conf.type      = 'dodge'
        conf.startup   = 0
        conf.recovery  = 0.7
       #conf.on_start  = None
       #conf.on_end    = None
        conf.cancel_by = ['s']


    def sync(this, c):
        this.type    = c.type
        this.startup = c.startup
        
        this.init()


class _Dodge(object):
    def __init__(this, name, host, conf=None):
        this.name = name
        this.host = host
        this.e_x = Event('cancel')

        this.conf = Conf_dodge(this, conf)

        this.ac = host.Action(this.name, this.conf)

        this.log = Logger('dodge')
        this.src = this.host.name+', '
        this.speed = host.speed # function


    def __call__(this):
        return this.tap()


    def init(this):
        this.e_x.name = this.name
        this.e_x.type = this.type
        this.e_x.idx = 0
        this.e_x.last = 0
        return this


    def tap(this):
        if this.log:
            this.log(this.src+this.name, 'tap')

        if this.ac():
            if this.log:
                this.log('start')
            return 1
        else:
            if this.log:
                this.log('failed')
            return 0



class Fs_group(object):
    def __init__(this, host, wtconf):
        this.host = host
        this.a_fs = [0,1,2,3,4,5,6]
        this.a_fs[0] = host.Fs('fs', host, wtconf.fs).init()
        for i in range(1, 6):
            fsname = 'x%dfs'%i
            if fsname in wtconf:
                tmp = Conf(wtconf.fs)
                tmp(wtconf[fsname])
                wtconf[fsname](tmp)
                this.a_fs[i] = host.Fs('fs', host, wtconf[fsname]).init()
            else:
                this.a_fs[i] = host.Fs('fs', host, wtconf.fs).init()
        if 'dfs' in wtconf:
            tmp = Conf(wtconf.fs)
            tmp(wtconf.dfs)
            wtconf.dfs(tmp)
            this.a_fs[6] = host.Fs('fs', host, wtconf.dfs).init()


    def __call__(this):
        doing = this.host.Action.doing.conf
        if doing.type == 'x':
            this.a_fs[doing.idx]()
        elif doing.type == 'dodge':
            this.a_fs[6]()
        else:
            this.a_fs[0]()
    

    def init():
        return this

