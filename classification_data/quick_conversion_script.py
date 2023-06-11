import json


def main():
    with open('certain_existence.json') as file:
        certain = json.load(file)

    with open('life.json') as file:
        non_certain = json.load(file)

    new_tag_system = [{}, {}, {}, {}, {}]

    for tag, include_rule in certain.items():
        if include_rule:
            new_tag_system[0][tag] = {
                'Description': {
                    'Includes': include_rule
                }
            }

    for tag, include_rule in non_certain.items():
        if include_rule:
            new_tag_system[0][tag] = {
                'Description': {
                    'Includes': include_rule
                }
            }

    new_tag_system[1]['Automatic'] = {
        'Tags': {
            'Any': list(certain.keys())
        }
    }

    new_tag_system[2]['existence'] = {
        'Tags': {
            'Any': ['Automatic']
        }
    }

    new_tag_system[3]['life'] = {
        'Tags': {
            '~Has': 0,
            '~Any': ['existence']
        }
    }

    new_tag_system[4]['existence'] = {
        'Tags': {
            '~Any': ['existence', 'life']
        }
    }

    with open('tag_rules.json', 'w') as file:
        json.dump(new_tag_system, file)


if __name__ == '__main__':
    main()
