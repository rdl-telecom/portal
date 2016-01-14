default_name='unknown-system'

def get_system_name(filename):
    name = default_name
    try:
        with open(filename, 'r') as f:
            name = f.read().strip('\n')
    except:
        pass
    return name
