import ast
import logging
import os

import pandas as pd

from configuration import get_filepaths
from helper_functions import ensure_dir_exists
from structures import database_types, merged_types, off_record_types


class DataBase:
    suffixes = (' input', ' merged')

    def __init__(self):
        self.__path = get_filepaths()['database']

    def run_on_main(self, gui=False):
        confirmation = True
        if not gui:
            confirmation = input('I know what I am doing! I want to run on main database: ') == 'yes'

        if confirmation:
            self.__path = os.path.join(self.__path, 'protected')
        else:
            raise FileNotFoundError('Remove run on main!')

    def run_not_on_main(self):
        self.__path = get_filepaths()['database']

    def get_database(self):
        database = self._read_csv('all.csv')
        if database is None:
            return pd.DataFrame({name: pd.Series(dtype=column_type) for name, column_type in database_types.items()})
        database['ref'] = database.index
        database = database.astype(database_types)
        database = database.sort_values(by='Date')
        return database

    def get_merged(self):
        merged = self._read_csv('merged.csv')
        if merged is None:
            return pd.DataFrame({name: pd.Series(dtype=column_type) for name, column_type in merged_types.items()})
        merged['Tags'] = merged['Tags'].apply(lambda x: ast.literal_eval(x))
        return merged.astype(merged_types)

    def get_joined(self):
        data = self.get_database()
        merged = self.get_merged()
        return data.merge(merged, on='ref', suffixes=self.suffixes)

    def get_off_record(self):
        cash = self._read_csv('cash.csv')
        if cash is None:
            return pd.DataFrame({name: pd.Series(dtype=column_type) for name, column_type in off_record_types.items()})
        return cash.astype(merged_types)

    def _read_csv(self, filename):
        try:
            return pd.read_csv(os.path.join(self.__path, filename), index_col='key')
        except FileNotFoundError:
            logging.error(f'Attempt to read file "{filename}", which does not exist.')
            return None

    def add_to_database(self, new_items: pd.DataFrame):
        old_items = self.get_database()

        old_items = old_items.drop('ref', axis=1)
        new_items = new_items.drop('ref', axis=1)

        self._add_new_items(old_items, new_items, 'all')

    def add_to_merged(self, new_items: pd.DataFrame):
        old_items = self.get_merged()
        self._add_new_items(old_items, new_items, 'merged')

    def add_to_off_record(self, new_items: pd.DataFrame):
        old_items = self.get_off_record()
        self._add_new_items(old_items, new_items, 'off_record')

    def _add_new_items(self, old_items, new_items: pd.DataFrame, where):
        if len(new_items):
            # Load and back-up
            previous_path = os.path.join(self.__path, f'previous_{where}.csv')
            ensure_dir_exists(previous_path)
            old_items.to_csv(previous_path)

            # Merge and Save
            new_database = pd.concat([old_items, new_items], ignore_index=True)

            new_database.index.name = 'key'
            path = os.path.join(self.__path, f'{where}.csv')
            ensure_dir_exists(path)
            new_database.to_csv(path)

            logging.info(f'Saved {where} with {len(new_items)} new rows')
        else:
            logging.info(f'Tried to add an empty table')

    def reset_database(self):
        old_items = self.get_database()
        old_items.to_csv(os.path.join(self.__path, 'previous_all.csv'))
        with open(os.path.join(self.__path, 'all.csv'), 'w+') as file:
            file.write('key,Date,Type,Description,Value,Balance,Account Name,Account Number')
            logging.warning(f'Just reset merged at {self.__path}/previous_all.csv')

    def reset_merged(self):
        old_items = self.get_merged()
        old_items.to_csv(os.path.join(self.__path, 'previous_merged.csv'))
        with open(os.path.join(self.__path, 'merged.csv'), 'w+') as file:
            file.write('key,ref,Who,What,Description,Amount,Sub Account')
            logging.warning(f'Just reset merged at {self.__path}/previous_merged.csv')
