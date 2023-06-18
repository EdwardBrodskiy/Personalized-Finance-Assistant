import json
import os


def get_filepaths():
    filepaths = try_get_config('filepaths.json')
    joined_filepaths = {key: os.path.join(*path) for key, path in filepaths.items()}
    return joined_filepaths


def get_tag_rules():
    return try_get_config('tag_rules.json')


def get_transaction_formats():
    return try_get_config('transaction_formats.json')


def try_get_config(filename):
    try:
        with open(os.path.join('config', filename)) as file:
            data = json.load(file)
    except FileNotFoundError:
        try:
            with open(os.path.join('default_config', filename)) as file:
                data = json.load(file)
            if not os.path.exists('config'):
                os.makedirs('config')
            with open(os.path.join('config', filename), 'w+') as file:
                json.dump(data, file, indent=2)
        except FileNotFoundError:
            raise FileNotFoundError(
                f'Default config for {filename} is missing. It is not recommended to '
                f'change the default config. Restore default config and edit config instead.')
    return data
