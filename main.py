import pandas as pd
import logging

from indexer import index as index_input_data
from sheets_importer import main as import_sheets_labels
from classifier import Classifier
from database import DataBase


def reset_db():
    db = DataBase()
    db.reset_database()
    db.reset_merged()

    index_input_data()
    import_sheets_labels()
    classify_and_save()


def classify_and_save():
    cl = Classifier()
    auto_labeled, manual_labeled, un_labeled = cl.classify()
    db = DataBase()
    db.add_to_merged(auto_labeled)
    # db.add_to_merged(manual_labeled)
    logging.info(f'These were left un labeled:\n{un_labeled}')


def main():
    options = {
        'reset': reset_db
    }
    entry = input(f'{options}\nWhat do you want to do?')
    options[entry]()


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    logging.basicConfig(filename='logs/indexer.log', filemode='a',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
