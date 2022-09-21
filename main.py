import pandas as pd
import logging

from indexer import index as index_input_data
from sheets_importer import main as import_sheets_labels
from classifier import Classifier
from database import DataBase


def reset_db(db):
    db.reset_database()
    db.reset_merged()

    index_input_data()
    import_sheets_labels()
    classify_and_save(db)


def classify_and_save(db):
    cl = Classifier()
    auto_labeled, manual_labeled, un_labeled = cl.classify()
    db.add_to_merged(auto_labeled)
    db.add_to_merged(manual_labeled)
    logging.info(f'These were left un labeled:\n{un_labeled}')


def ingest_new_data(db):
    index_input_data()
    classify_and_save(db)


def copy_from_protected(_):
    import shutil
    from os.path import join
    entry = input('copy all.csv, merged.csv or both?(a, m, b)')
    if entry in ('a', 'b'):
        shutil.copy2(join('database', 'protected', 'all.csv'), join('database', 'all.csv'))
    if entry in ('m', 'b'):
        shutil.copy2(join('database', 'protected', 'merged.csv'), join('database', 'merged.csv'))


def main():
    options = {
        'reset': reset_db,
        'ingest': ingest_new_data,
        'not test': lambda data_base: data_base.run_on_main(),
        'copy main': copy_from_protected,
        'finish': lambda: print('hmm this should not be called'),

    }
    db = DataBase()
    while True:
        entry = input(f'{" | ".join(options.keys())}\nWhat do you want to do?')
        if entry == 'finish':
            break
        if entry in options:
            options[entry](db)
        else:
            print('No such command found!')


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    logging.basicConfig(filename='logs/indexer.log', filemode='a',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
