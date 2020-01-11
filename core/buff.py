import __init__
from core.ctx import *


class Passive(object):
    def __init__(this, Dp):
        this.Dp = Dp
        this.hostname = Dp.host.name


    def __call__(this, *args, **kwargs):
        return _Passive(this, *args, **kwargs)


class _Passive():
    def __init__(this, static, name, value, mtype='atk', morder=None):
        this._static = static
        this.name = name
        this._value = value
        this.mod_type = mtype # atk def_ cc cd buff sp x fs s dmg killer ks
        if morder == None:
            this.mod_order = 'p'
        else:
            this.mod_order = morder # p: passive, b: buff, ex: co-ab, 
            # od, bk, burn, poison...  (mtype = killer/ks)

        this._active = 0
        this.Dp = this._static.Dp
        this.dp = this._static.Dp(this.name,
                this.mod_type, this.mod_order, value)

        this.log = Logger('buff')
        this.on_end = []

    def hostname(this):
        return this._static.hostname


    def on(this):
        if this._active :
            this.dp()
            if this.log:
                this.log(this.hostname(), this.name,
                    '%s: %.2f'%(this.mod_type, this._value),'refresh')
            return this
        this.dp()
        this._active = 1
        if this.log:
            this.log(this.hostname(), this.name,
                '%s: %.2f'%(this.mod_type, this._value),'on <passive>')
        return this

    __call__ = on


    def off(this):
        if not this._active :
            return
        this.dp.off()
        this._active = 0
        if this.log:
            this.log(this.hostname(), this.name,
                '%s: %.2f'%(this.mod_type, this._value),'off <passive>')
        for i in this.on_end:
            i()


    def get(this):
        if this._active:
            return this._value
        else:
            return 0


    def set(this, v):
        this._value = v
        this.dp.set(v)
        if this.log:
            this.log(this.hostname(), this.name,
                '%s: %.2f'%(this.mod_type, this._value),'set')
        return this


class Buff(object):
    def __init__(this, Dp):
        this.Dp = Dp
        this.host = Dp.host
        this.hostname = Dp.host.name

        this.buff_group = {}

        this.listener = Listener('buff')(this.l_buff)
        this.log = Logger('buff')


    def __call__(this, *args, **kwargs):
        return _Buff(this, *args, **kwargs)


    def l_buff(this, e):
        this(e.src+'_'+e.name, e.value, e.mtype, e.morder, e.group)(e.duration)


class _Buff(object):
    bufftype = 'buff'
    def __init__(this, static, name, value, mtype='atk', morder=None, group=None):
        this._static = static
        if morder == None:
            if mtype in ['atk','hp','sd']:
                morder = 'b'
            else:
                morder = 'p'
        this.name = name
        this._value = value
        this.mod_type = mtype   # atk def_ cc cd bt sp x fs sd dmg
        this.mod_order = morder # p: passive, b: buff, k: killer, ex: co-ab
        if group == None:
            this.group_name = mtype
        else:
            this.group_name = group
        group_id = (this.group_name, this.mod_order)

        this._active = 0
        this.t_buffend = Timer(this.__buff_end)
        this.Dp = this._static.Dp
        if this.mod_type in this.Dp.type_mods:
            this.dp = this.Dp(this.name, this.mod_type, this.mod_order, value)
        else:
            this.dp = this.Dp(this.name, '', this.mod_order, value)
        if group_id not in this._static.buff_group:
            this.group = []
            this._static.buff_group[group_id] = this.group
        else:
            this.group = this._static.buff_group[group_id]

        this.bt_cache = this.Dp.cache
        this.bt_get = this.Dp.get_

        this.log = Logger('buff')
        this.log_dp = Logger('dp')

        this.e_on = static.host.Event('buff')
        this.e_on.btype = mtype

        this.on_end = []

    def hostname(this):
        return this._static.hostname

    def append(this, length):
        if this.t_buffend.timing > 0:
            this.t_buffend.timing += length
            if this.log :
                this.log(this.hostname(), this.name,
                        '%s: %.2f'%(this.mod_type, this.get()),
                        '%s %s append +%ss'%(this.group_name,
                            this.bufftype, length))

    def get(this):
        if this._active:
            return this._value
        else:
            return 0


    def set(this, v):
        #if this._active:
        #    print('can not set buff when active')
        #    raise
        this._value = v
        this.dp.set(this._value)
        if this.log :
            this.log(this.hostname(), this.name,
                    '%s: %.2f'%(this.mod_type, this.get()),
                    '%s %s set'%(this.group_name,
                        this.bufftype))
        if this.log_dp:
            if this.mod_type in this._static.Dp.type_mods:
                this.log_dp(this.hostname(), this.mod_type,
                        this._static.Dp.get(this.mod_type))
        return this


    def get_group(this):
        value = 0
        stack = len(this.group)
        for i in this.group :
            if i._active != 0:
                value += i._value
        return value, stack


    def __buff_stack(this):
        v_total, stacks = this.get_group()
        this.log(this.hostname(), this.name,
            '%s stack: %d'%(this.group_name, stacks),
            'total: %.2f'%(v_total))


    def __buff_start(this, duration):
        this._active = 1
        this.dp.on()
        if duration > 0:
            this.t_buffend(duration)
        stacks = len(this.group)
        if stacks >= 10:
            if this.log:
                this.log(this.hostname(), this.name,
                    'failed', 'stack cap')
            return
        stacks += 1
        this.group.append(this)
        if this.log:
            this.log(this.hostname(), this.name,
                    '%s: %.2f'%(this.mod_type, this.get()),
                    '%s %s start <%ss>'%(this.group_name,
                        this.bufftype, duration))
            if stacks > 1:
                this.__buff_stack()
        if this.log_dp:
            if this.mod_type in this._static.Dp.type_mods:
                this.log_dp(this.hostname(), this.mod_type,
                        this._static.Dp.get(this.mod_type))


    def __buff_refresh(this, duration):
        if duration > 0:
            this.t_buffend.on(duration)
        if this.log :
            this.log(this.hostname(), this.name,
                    '%s: %.2f'%(this.mod_type, this.get()),
                    '%s %s refresh <%ss>'%(this.group_name,
                        this.bufftype, duration))
            stacks = len(this.group)
            if stacks > 1:
                this.__buff_stack()


    def __buff_end(this, e):
        this._active = 0

        idx = len(this.group)
        stack = idx
        while 1:
            idx -= 1
            if idx < 0:
                break
            if this == this.group[idx]:
                this.group.pop(idx)
                break
        if this.log:
            this.log(this.hostname(), this.name,
                    '%s: %.2f'%(this.mod_type, this._value),
                    '%s end <timeout>'%this.bufftype)
            if stack > 1:
                this.__buff_stack()
        this.dp.off()
        for i in this.on_end:
            i()
        if this.log_dp:
            if this.mod_type in this._static.Dp.type_mods:
                this.log_dp(this.hostname(), this.mod_type,
                        this._static.Dp.get(this.mod_type))

    def on(this, duration):
        this.duration = duration
        if this._active == 0:
            this.__buff_start(duration)
            this.e_on()
        else:
            this.__buff_refresh(duration)

        return this

    __call__ = on


    def off(this):
        if this._active == 0:
            return
        if this.log:
            this.log(this.hostname(), this.name,
                '%s: %.2f'%(this.mod_type, this.get()),
                '%s %s end <turn off>'%(this.name, this.duration))
        this._active = 0

        idx = len(this.group)
        while 1:
            idx -= 1
            if idx < 0:
                break
            if this == this.group[idx]:
                this.group.pop(idx)
                break
        this.dp.off()
        if this.log:
            this.__buff_stack()
        this.t_buffend.off()
        for i in this.on_end:
            i()
        return this


class Selfbuff(object):
    def __init__(this, Buff):
        this.Buff = Buff


    def __call__(this, *args, **kwargs):
        return _Selfbuff(this.Buff, *args, **kwargs)



class _Selfbuff(_Buff):
    bufftype = 'selfbuff'
    def on(this, duration):
        # duration *= this.Dp.get('bt') {
        if this.bt_cache['bt'] >= 0:
            bt = this.bt_cache['bt']
        else:
            bt = this.bt_get('bt')
        duration *= bt
        # } duration *= this.Dp.get('bt')
        super().on(duration)
        return this

    __call__ = on


class Debuff(object):
    def __init__(this, Buff):
        this.Buff = Buff


    def __call__(this, *args, **kwargs):
        return _Debuff(this.Buff, *args, **kwargs)


class _Debuff(_Buff):
    bufftype = 'debuff'
    def __init__(this, static, name, value, mtype='def', morder=None, group=None):
        super().__init__(static, name, 0-value, mtype, morder, group)
        #this.dp.set(0.0-value)
        

    def set(this, v):
        if this._active:
            print('can not set buff when active')
            raise
        this._value = 0.0-v
        this.dp.set(this._value)
        return this


class Teambuff(object):
    def __init__(this, Buff):
        this.hostname = Buff.hostname
        this.Dp = Buff.Dp
        this.e = Event('buff')


    def __call__(this, *args, **kwargs):
        return _Teambuff(this, *args, **kwargs)


class _Teambuff():
    bufftype = 'teambuff'
    def __init__(this, static, name, value,
            mtype='atk', morder=None, group=None):
        this._static = static
        e = static.e
        e.src = static.hostname
        e.name = name
        e.value = value
        e.mtype = mtype
        e.morder = morder
        e.group = group

        this.e = e
        this.Dp = this._static.Dp
        this.bt_cache = this.Dp.cache
        this.bt_get = this.Dp.get_
        this.log = Logger('buff')


    def on(this, duration):
        # this.e.duration = duration * this.Dp.get('bt') {
        if this.bt_cache['bt'] >= 0:
            bt = this.bt_cache['bt']
        else:
            bt = this.bt_get('bt')
        this.e.duration = duration * bt
        # this.e.duration = duration * this.Dp.get('bt') }
        this.e()
        return this

    __call__ = on


    def set(this, v):
        this.e.value = v
        return this


class Zonebuff(object):
    def __init__(this, Buff):
        this.hostname = Buff.hostname
        this.Dp = Buff.Dp
        this.e = Event('buff')


    def __call__(this, *args, **kwargs):
        return _Zonebuff(this, *args, **kwargs)


class _Zonebuff():
    bufftype = 'buffzone'
    def __init__(this, static, name, value,
            mtype='atk', morder=None, group=None):
        this._static = static
        e = static.e
        e.src = static.hostname
        e.name = name
        e.value = value
        e.mtype = mtype
        e.morder = morder
        e.group = group

        this.e = e
        this.Dp = this._static.Dp
        this.log = Logger('buff')


    def on(this, duration):
        this.e.duration = duration
        this.e()
        return this

    __call__ = on


    def set(this, v):
        this.e.value = v
        return this


class Selfzone(object):
    def __init__(this, Buff):
        this.Buff = Buff

    def __call__(this, *args, **kwargs):
        return _Selfbuff(this.Buff, *args, **kwargs)

class _Selfzone(_Buff):
    bufftype = 'selfzone'
    def on(this, duration):
        super().on(duration)
        return this

    __call__ = on


class ToggleBuff(object):
    def __init__(self, Buff):
        self.Buff = Buff

        self.buff_dict = {}


    def __call__(self, name, *args, **kwargs):
        if name not in self.buff_dict:
            self.buff_dict[name] = _ToggleBuff(self.Buff, name, *args, **kwargs)
        return self.buff_dict[name]


class _ToggleBuff():
    bufftype = 'togglebuff'
    def __init__(self, static, name, *args, **kwargs):
        self.buffs = []
        self.c_idx = None
        for idx, b in enumerate(args[0]):
            if not b:
                self.buffs.append(None)
            else:
                wide = b[0]
                value = b[1]
                time = b[2]
                buffarg = b[3:]
                if wide == 'self':
                    self.buffs.append((_Selfbuff(static, '{}_buff_{}'.format(name, idx+1), value, *buffarg), time))
                elif wide == 'team':
                    self.buffs.append((_Teambuff(static, '{}_buff_{}'.format(name, idx+1), value, *buffarg), time))

    def on(self):
        if self.c_idx is None:
            self.c_idx = 0
        else:
            if self.buffs[self.c_idx]:
                buff, _ = self.buffs[self.c_idx]
                buff.off()
            self.c_idx = (self.c_idx + 1) % len(self.buffs)
        if self.buffs[self.c_idx]:
            buff, time = self.buffs[self.c_idx]
            return buff.on(time)
        else:
            return None

    def get_buff_by_idx(self, idx):
        if self.buffs[idx]:
            buff, _ = self.buffs[idx]
            return buff
        else:
            return None

    __call__ = on


if __name__ == '__main__':
    pass
