import pandas as pd
import logging


class DataBase:
    @staticmethod
    def get_database():
        return pd.read_csv('database/all.csv', index_col='key')

    @staticmethod
    def add_to_database(new_items: pd.DataFrame):
        if len(new_items):
            # Load and back-up
            database = DataBase.get_database()
            database.to_csv('database/previous_all.csv')

            # Merge and Save
            new_database = pd.concat([database, new_items], ignore_index=True)
            new_database.index.name = 'key'
            new_database.to_csv('database/all.csv')

            logging.info(f'Saved database with {len(new_items)} new rows')
        else:
            logging.info(f'Tried to add an empty table')
