import pandas as pd
import logging
from structures import database_types, merged_types
import os


class DataBase:
    def __init__(self):
        self.__path = 'database'

    def run_on_main(self):
        if input('I know what I am doing! I want to run on main database: ') == 'YES':
            self.__path = 'database/protected'
        raise FileNotFoundError('Remove run on main!')

    def get_database(self):
        database = pd.read_csv(f'{self.__path}/all.csv', index_col='key')
        return database.astype(database_types)

    def get_merged(self):
        database = pd.read_csv(f'{self.__path}/merged.csv', index_col='key')
        return database.astype(merged_types)

    def add_to_database(self, new_items: pd.DataFrame):
        old_items = self.get_database()
        self._add_new_items(old_items, new_items, 'all')

    def add_to_merged(self, new_items: pd.DataFrame):
        old_items = self.get_merged()
        self._add_new_items(old_items, new_items, 'merged')

    def _add_new_items(self, old_items, new_items: pd.DataFrame, where):
        if len(new_items):
            # Load and back-up

            old_items.to_csv(f'{self.__path}/previous_{where}.csv')

            # Merge and Save
            new_database = pd.concat([old_items, new_items], ignore_index=True)

            new_database.index.name = 'key'
            new_database.to_csv(f'{self.__path}/{where}.csv')

            logging.info(f'Saved {where} with {len(new_items)} new rows')
        else:
            logging.info(f'Tried to add an empty table')
