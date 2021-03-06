import random
from mod.dot import *


class Afflic(object):
    def __init__(this, src):
        this.src = src
        this.dst = src.target
        if 'Afflics' not in this.dst.mod:
            this.dst.mod['Afflics'] = Afflics(this.dst)

    def __call__(this, name, atype, *args, **kwargs):
        return this.dst.mod['Afflics'](atype, this.src, name, *args, **kwargs)
    
    def __getitem__(this, atype):
        return _Afflic(this, atype)
        

class _Afflic(object):
    def __init__(this, static, atype):
        this._static = static
        this.atype = atype

    def __call__(this, name, *args, **kwargs):
        return this._static.dst.mod['Afflics'](this.atype, this._static.src,
                                                name, *args, **kwargs)

class Afflics(object):
    def __init__(this, host):
        this.host = host
        if 'Dot_group' not in this.host.mod:
            host.mod['Dot_group'] = Dot_group(host)
        this.dot_group = {
                 'burn'      : None
                ,'poison'    : None
                ,'paralysis' : None
                }
        this.scc = {
                 'blind' : None
                ,'bog'   : None
                }
        this.cc = None

        this.log = Logger('afflic')
        this.iv_default = {
                 'burn'      : 3.99
                ,'poison'    : 2.99
                ,'paralysis' : 3.99
                }
        this.duration_default = {
                 'burn'      : 12
                ,'poison'    : 15
                ,'paralysis' : 13
                ,'blind'     : 8
                ,'bog'       : 8
                ,'freeze'    : 4.5
                ,'stun'      : 6.5
                ,'sleep'     : 6.5
                }


    def __call__(this, atype, *args, **kwargs): # src, name, coef, duration):
        if atype == 'burning' :
            atype = 'burn'
        if atype == 'para':
            atype = 'paralysis'
        if atype in ['poison','burn','paralysis']:
            return _Afflic_dot(this, atype, *args, **kwargs)
        elif atype in ['blind','bog']:
            return _Afflic_scc(this, atype, *args, **kwargs)
        elif atype in ['freeze', 'stun','sleep']:
            return _Afflic_cc(this, atype, *args, **kwargs)


    def reset(this):
        if this.log:
            this.log(this.host.name, 'clean')
        for i in this.dot_group:
            if this.dot_group[i]:
                this.dot_group[i].reset()
        for i in this.scc:
            if this.scc[i]:
                this.scc[i].reset()
                this.scc[i] = None
        if this.cc:
            for i in this.cc:
                this.cc[i].reset()
            this.cc = None


class _Afflic_dot():
    def __init__(this, static, atype, src, name, rate, coef, duration=None):
        this._static = static
        this.rate = rate
        this.src = src
        this.name =name
        this.coef = coef
        host = static.host
        this.host = host
        this.resist = host.resist
        if not static.dot_group[atype] :
            static.dot_group[atype] = host.mod['Dot_group'](atype,
                                        static.iv_default[atype])
        this.atype = atype
        this.coef = coef
        if duration:
            this.duration = duration
        else:
            this.duration = static.duration_default[atype]

        this.dot = static.dot_group[atype]
        this.log = Logger('afflic')
        this.e_afflic = this.src.Event('afflic')
        this.e_afflic.atype = atype

    def on(this):
        if this.resist[this.atype] >= 1:
            if this.log:
                this.log(this.host.name, 'perfect resist')
            return 
        if random.random() < this.rate-this.resist[this.atype] :
            # proc
            if this.log:
                this.log(this.host.name, 'proc', '%.2f - %.2f'%(this.rate,
                                                this.resist[this.atype]) )
            this.resist[this.atype] += 0.05
            this.dot(this.src, this.name, this.coef, this.duration)()
            this.e_afflic()
        else:
            # resist
            if this.log:
                this.log(this.host.name, 'normal resist')

    __call__ = on


class _Afflic_scc():
    def __init__(this, static, atype, src, name, rate, duration=None):
        this._static = static
        this.atype = atype
        this.src = src
        this.name =name
        this.rate = rate
        if duration:
            this.duration = duration
        else:
            this.duration = static.duration_default[atype]

        host = static.host
        this.resist = host.resist

        this.ks = host.Buff('ks_%s'%atype, 1, 'ks', atype)
        this.ks.on_end.append(this.cb_end)

        this.log = Logger('afflic')
        if atype == 'blind':
            this.tolerance = 0.1
            this.debuff = None
        elif atype == 'bog':
            this.tolerance = 0.2
            this.debuff = host.Buff('bog', 0.5, 'dt')
        else:
            print('only blind and bog in soft cc')
            raise
        this.e_afflic = this.src.Event('afflic')
        this.e_afflic.atype = atype

    def reset(this):
        this.ks.off()
        if this.debuff:
            this.debuff.off()


    def cb_end(this):
        this._static.scc[this.atype] = None

    def on(this):
        if this.resist[this.atype] >= 1:
            if this.log:
                this.log(this.host.name, 'perfect resist')
            return 
        if random.random() < this.rate-this.resist[this.atype] :
            # proc
            if this._static.scc[this.atype]:
                if this.log:
                    this.log(this.host.name, 'faild','active already')
                return

            if this.log:
                this.log(this.host.name, 'proc', '%.2f - %.2f'%(this.rate, this.resist[this.atype]) )

            this._static.scc[this.atype] = this
            this.resist[this.atype] += this.tolerance
            this.ks(this.duration)
            if this.debuff:
                this.debuff(this.duration)
            this.e_afflic()
        else:
            # resist
            if this.log:
                this.log(this.host.name, 'normal resist')

    __call__ = on


class _Afflic_cc():
    def __init__(this, static, atype, src, name, rate, duration=None):
        this._static = static
        this.atype = atype
        this.src = src
        this.name =name
        this.rate = rate
        if duration:
            this.duration = duration
        else:
            this.duration = static.duration_default[atype]

        host = static.host
        this.resist = host.resist

        this.ks = host.Buff('ks_%s'%atype, 1, 'ks', atype)
        this.ks.on_end.append(this.cb_end)

        this.log = Logger('afflic')
        this.e_afflic = this.src.Event('afflic')
        this.e_afflic.atype = atype

    def reset(this):
        this.ks.off()

    def cb_end(this):
        this._static.cc = None

    def on(this):
        if this.resist[this.atype] >= 1:
            if this.log:
                this.log(this.host.name, 'perfect resist')
            return 
        if random.random() < this.rate-this.resist[this.atype] :
            # proc
            while(1): # make a goto
                if not this._static.cc:
                    break
                elif this.atype in this._static.cc:
                    if this.log:
                        this.log(this.host.name, 'faild','active already')
                    return
                else:
                    for i in this._static.cc:
                        this._static.cc[i].reset()
                        if this.log:
                            this.log(this.host.name, 'cover %s'%i , 'by %s'%this.atype )
                    break

            if this.log:
                this.log(this.host.name, 'proc', '%.2f - %.2f'%(this.rate,
                                                this.resist[this.atype]) )

            this._static.cc = {this.atype: this}
            this.resist[this.atype] += 0.2
            this.ks(this.duration)
            this.e_afflic()
        else:
            # resist
            if this.log:
                this.log(this.host.name, 'normal resist')

    __call__ = on


