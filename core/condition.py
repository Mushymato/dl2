

_g_cond = 0


class Condition(object):

    def __init__(this):
        this.if_condition = True
        this.conditions = {}
        this.switch = -1


    def set(this, c=True):
        this.if_condition = c


    def unset(this):
        this.if_condition = False


    def __str__(this):
        a = this.conditions
        ret = ''
        for i in a:
            if ret != '':
                ret += ' & '
            ret += i
        if not this.if_condition:
            ret = 'NOT '+ret
        return ret


    def __call__(this, cond):
        if cond not in this.conditions:
            this.conditions[cond] = 1
        else:
            this.conditions[cond] += 1

        if this.switch == -1 :
            this.switch = this.if_condition
        elif this.switch != this.if_condition:
            print('condition_do not match same condition' )
            errrrrrrrrrrr()

        return this.if_condition
    on = __call__


if __name__ == '__main__':
    a = Condition()
    print(a('test1'))
    print(a('test2'))
    print(a('test3'))
    print(a)
