import csv
import pandas as pd
import numpy as np
from structures import mp
import logging
from database import DataBase


def main():
    index()


def get_items_from_input():
    all_items = []
    for year in range(2019, 2200):
        try:
            with open(f'input/{year}.csv') as file:

                reader = csv.reader(file)

                for index, row in enumerate(reader):
                    if len(row) == len(mp) + 1:
                        all_items.append(row[:-1])
        except FileNotFoundError:
            logging.info(f'found years up to {year - 1}')
            break

    items_table = pd.DataFrame(data=all_items, columns=list(mp.keys()))
    items_table['Value'] = items_table['Value'].astype(np.float64)
    items_table['Balance'] = items_table['Balance'].astype(np.float64)
    items_table = items_table.replace(r'^\s*$', np.nan, regex=True)
    items_table.index.name = 'key'
    return items_table


def find_new(df1, df2):
    return df1[~df1.apply(tuple, 1).isin(df2.apply(tuple, 1))]


def index():
    incoming_table = get_items_from_input()
    current_table = DataBase.get_database()

    new = find_new(incoming_table, current_table)

    logging.info(f'\nFound these new entries:\n{new}')

    DataBase.add_to_database(new)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    logging.basicConfig(filename='logs/indexer.log', filemode='a',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.info('\n\n### RUNNING indexer.py ###\n')
    main()
