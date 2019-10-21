from core.ctx import *
from core.skada import *
import copy
from core import env

def loglevel(level):
    if level == 0:
        logset([])
    elif level == 1:
        logset(['buff', 'dmg', 'sp', 'rotation'])
    elif level == 2:
        logset(['all'])
    elif level == -1:
        logset(['rotation'])
    elif level == -2:
        logset([])
        
def show_rotation():
    logcat(['rotation'])

def show_log():
    logcat()

def show_detail():
    Skada.sum()
    print(Skada._skada)

def show_csv():
    line = ''
    t = 0
    for i,v in Skada._skada.items():
        if i[0] != '_':
            d = v['dmg']
    for i, v in Skada.sum(q=1).items():
        if i[0] != '_':
            total = v['dmg']
            name = i
        else:
            t = v['dmg'] - 10000
            total += t
    line += '%s,%s,'%(total, name)

    info = ''
    l = logget()
    for i in l:
        if i[1]=='info' and i[3]=='setup' and i[2][0]!='_':
            info = i[4]
    if 'range' in env.root:
        if env.root['range']['min'][name] > 0:
            info += ';dpsrange:(%d~%d)'%(env.root['range']['min'][name],
                        env.root['range']['max'][name] )

    line+=info+','

    combo = 0
    fs = 0
    s1 = 0
    s2 = 0
    s3 = 0
    dd = copy.copy(d)
    for i in dd:
        v = d[i]
        if i[0] == 'x':
            combo += v
            del(d[i])
    if 'fs' in d:
        fs = d['fs']
        del(d['fs'])
    if 's1' in d:
        s1 = d['s1']
        del(d['s1'])
    if 's2' in d:
        s2 = d['s2']
        del(d['s2'])
    if 's3' in d:
        s3 = d['s3']
        del(d['s3'])
    tb = t

    line += 'attack:%s,force_strike:%s,skill_1:%s,skill_2:%s,skill_3:%s,team_buff:%s'%(combo, fs, s1, s2, s3, tb)
    for i in d:
        line += ',%s:%s'%(i, d[i])

    print(line)

