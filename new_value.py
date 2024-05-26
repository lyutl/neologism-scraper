"""
New definition checker
"""


def has_new_value(table, name):
    try:
        new_name = table.find('span', {
            'class': 'field field--name-title field--type-string field--label-hidden'}).text.strip()
    except AttributeError:
        new_name = ''

    return new_name == name
