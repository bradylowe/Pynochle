

def num_to_str(num):
    if num >= 1000000000:
        return f'{int(num // 1000000000)}G'
    elif num >= 1000000:
        return f'{int(num // 1000000)}M'
    elif num >= 1000:
        return f'{int(num // 1000)}K'
    else:
        return str(num)
