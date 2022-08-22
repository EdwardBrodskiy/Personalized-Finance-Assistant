import json

with open('classification_data/certain_existence.json') as file:
    existence_keys = json.load(file)

new = {}

for key, value in existence_keys.items():
    if value not in new:
        new[value] = []
    new[value].append(key)

with open('classification_data/certain_existencet.json', 'w+') as file:
    json.dump(new, file)