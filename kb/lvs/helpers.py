def full_name(node):
    full = ''
    
    first = _tag_string(node.roepnaam)
    if first == '':
        first = _tag_string(node.voornamen)
    if first == '':
        first = _tag_string(node.voorletters)
    full += first +' '

    prefix = _tag_string(node.voorvoegsel)
    if prefix != '':
        full += prefix +' '

    full += _tag_string(node.achternaam)

    return full

def _tag_string(node):
    from bs4 import element
    if type(node) is element.Tag:
        return node.string.strip()
    return ''

def generate_email(node, form, domain): 
    email = ''

    first = _tag_string(node.roepnaam).lower()
    if first == '':
        first = _tag_string(node.voornamen).lower()

    if form['first_name'] == 'none':
        return email
    elif form['first_name'] == 'name':
        email += first
    elif form['first_name'] == 'letter':
        email += first[0]
    elif form['first_name'] == 'initials':
        email += _tag_string(node.voorletters).lower()
    email += form['separator']

    prefix = _tag_string(node.voorvoegsel).lower()
    if form['prefix'] and prefix != '':
        email += prefix + form['separator']

    email += _tag_string(node.achternaam).lower()

    email += '@' + domain

    return email
