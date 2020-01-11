
def get(ele, wt, stars=None):
    slot = {}

    if ele == 'flame':
        slot['d'] = 'Sakuya'
    elif ele == 'water':
        slot['d'] = 'Siren'
    elif ele == 'wind':
        slot['d'] = 'Vayu'
    elif ele == 'light':
        if wt == 'dagger' or wt == 'bow' or wt == 'wand':
            slot['d'] = 'Daikokuten'
        else:
            slot['d'] = 'Cupid'
    elif ele == 'shadow':
        slot['d'] = 'Shinobi'

    slot['a1'] = 'RR'
    slot['a2'] = 'BN'

    if wt == 'sword':
        slot['a1'] = 'TSO'
        slot['a2'] = 'BN'
    if wt == 'blade':
        slot['a1'] = 'RR'
        slot['a2'] = 'BN'
    if wt == 'dagger':
        if ele == 'water':
            slot['a1'] = 'TB'
            slot['a2'] = 'The_Prince_of_Dragonyule'
        elif ele == 'shadow':
            slot['a1'] = 'TB'
            slot['a2'] = 'Howling_to_the_Heavens'
        else:
            slot['a1'] = 'TB'
            slot['a2'] = 'LC'
    if wt == 'axe': 
        slot['a1'] = 'KFM'
        slot['a2'] = 'FitF'
    if wt == 'lance': 
        slot['a1'] = 'RR'
        slot['a2'] = 'BN'
    if wt == 'wand': 
        slot['a1'] = 'RR'
        slot['a2'] = 'FoG'
    if wt == 'bow':
        slot['a1'] = 'FP'
        slot['a2'] = 'DD'
    
    slot['w'] = 'c534_'+ele
    return slot

