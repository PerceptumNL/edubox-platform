def _full_name(node):
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
        return node.string.strip().lower()
    return ''

def _generate_email(node, form, domain): 
    email = ''

    first = _tag_string(node.roepnaam)
    if first == '':
        first = _tag_string(node.voornamen)

    if form['first_name'] == 'name':
        email += first
    elif form['first_name'] == 'letter':
        email += first[0]
    elif form['first_name'] == 'initials':
        email += _tag_string(node.voorletters)
    email += form['separator']

    prefix = _tag_string(node.voorvoegsel)
    if form['prefix'] and prefix != '':
        email += prefix + form['separator']

    email += _tag_string(node.achternaam)

    email += '@' + domain

    return email
