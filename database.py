import pandas as pd


class DataBase:
    @staticmethod
    def get_database():
        return pd.read_csv('database/all.csv', index_col='key')

    def add_to_database(self, entries):
        pass
