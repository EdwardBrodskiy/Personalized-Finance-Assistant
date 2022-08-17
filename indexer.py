import csv
import pandas as pd
import numpy as np
from structures import mp
import logging


def main():
    index()


def index():
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

    items_table = pd.DataFrame(data=all_items, columns= list(mp.keys()))
    items_table.index.name = 'key'
    items_table.to_csv('database/all.csv')


if __name__ == '__main__':
    logging.basicConfig(filename='logs/indexer.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
