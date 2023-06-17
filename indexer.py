import csv
import logging

import numpy as np
import pandas as pd

from structures import mp, database_types


def get_items_from_input():
    all_items = []
    for year in range(1800, 2200):
        try:
            with open(f'input/{year}.csv') as file:

                reader = csv.reader(file)

                for i, row in enumerate(reader):
                    if len(row) >= len(mp) and row[0] != 'Date':
                        all_items.append(row[:7])
        except FileNotFoundError:
            logging.info(f'found years up to {year - 1}')
            break

    items_table = pd.DataFrame(data=all_items, columns=list(mp.keys()))
    items_table['Date'] = pd.to_datetime(items_table['Date'], dayfirst=True)
    items_table['ref'] = items_table.index
    items_table = items_table.astype(database_types)

    items_table = items_table.replace(r'^\s*$', np.nan, regex=True)
    items_table.index.name = 'key'
    return items_table


def find_new(possibly_new, existing):
    df1 = possibly_new[['Date', 'Value', 'Balance']]
    df2 = existing[['Date', 'Value', 'Balance']]
    return possibly_new[~df1.apply(tuple, 1).isin(df2.apply(tuple, 1))]


def index(db):
    incoming_table = get_items_from_input()
    current_table = db.get_database()

    new = find_new(incoming_table, current_table)

    logging.info(f'\nFound these new entries:\n{new}')

    db.add_to_database(new)

    return new  # return intended for info based output only
