import ast
import logging
import os

import numpy as np
import pandas as pd

from configuration import get_filepaths, get_best_default
from helper_functions import ensure_dir_exists
from structures import database_types, merged_types, additional_database_types


class DataBase:
    suffixes = (' input', ' merged')

    def __init__(self):
        self.__path = get_filepaths()['database']
        self.__is_on_main = False

    def run_on_main(self, gui=False):
        confirmation = True
        if not gui:
            confirmation = input('I know what I am doing! I want to run on main database: ') == 'yes'

        if confirmation:
            self.__path = os.path.join(self.__path, 'protected')
            self.__is_on_main = True
        else:
            raise FileNotFoundError('Remove run on main!')

    def run_not_on_main(self):
        self.__path = get_filepaths()['database']
        self.__is_on_main = False

    @property
    def is_on_main(self):
        return self.__is_on_main

    def get_database(self):
        database = self._read_csv('all.csv')
        if database is None:
            return pd.DataFrame({name: pd.Series(dtype=column_type) for name, column_type in database_types.items()})
        database['ref'] = database.index

        # This initialization handles the case when a new column is added in config and is missing completely it does
        # not handle absent values incoming ingest data that is the responsibility of the indexer
        database = self._initialize_missing_columns(database, database_types)

        database = database.astype(database_types)
        return database

    def get_merged(self):
        merged = self._read_csv('merged.csv')
        if merged is None:
            return pd.DataFrame({name: pd.Series(dtype=column_type) for name, column_type in merged_types.items()})
        merged['Tags'] = merged['Tags'].apply(lambda x: ast.literal_eval(x))
        return merged.astype(merged_types)

    def get_joined(self, sort_on=None):
        data = self.get_database()
        merged = self.get_merged()
        joined = data.merge(merged, how='outer', on='ref', suffixes=self.suffixes)

        joined = joined.fillna({
            f'Description{self.suffixes[1]}': '',
            'Amount': joined['Value']
        })
        joined.loc[joined['Tags'].isnull(), 'Tags'] = joined.loc[joined['Tags'].isnull(), 'Tags'].apply(
            lambda x: ['unlabeled'])

        if sort_on is not None and sort_on in joined.columns:
            joined = joined.sort_values(by=sort_on)
        return joined

    def _initialize_missing_columns(self, df: pd.DataFrame, expected_columns):
        df = df.copy()
        for column in expected_columns:
            if column in additional_database_types:
                continue
            if column not in df.columns.tolist():
                df[column] = df['Source'].apply(lambda x: self._grab_best_default(x, column))
        return df

    @staticmethod
    def _grab_best_default(source, column):
        default = get_best_default(source, column)
        return default if default is not None else np.nan

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

    def _add_new_items(self, old_items, new_items: pd.DataFrame, where):
        if len(new_items):
            # Load and back-up
            previous_path = os.path.join(self.__path, f'previous_{where}.csv')
            ensure_dir_exists(previous_path, is_file=True)
            old_items.to_csv(previous_path)

            # Merge and Save
            new_database = pd.concat([old_items, new_items], ignore_index=True)

            new_database.index.name = 'key'
            path = os.path.join(self.__path, f'{where}.csv')
            ensure_dir_exists(path, is_file=True)
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
