def get_time(text):
    mods = { 'S' : 1, 'M' : 60, 'H' : 3600 }
    seconds = 0
    if text.isdigit():
        seconds = int(text)
    else:
        num = text[:-1]
        suffix = text[-1].upper()
        if not num.isdigit():
            raise ValueError('Invalid time string: "{}"'.format(text))
        if suffix not in mods.keys():
            raise ValueError('Unknown modifier {} in time string: "{}"'
                             .format(suffix, text))
            seconds = int(num) * mods[suffix]
	return seconds
