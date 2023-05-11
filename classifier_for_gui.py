from structures import merged_types, database_types
import json
import pandas as pd
import numpy as np
from itertools import zip_longest
import math


class Classifier:
    expected_fields = ('ref', 'Who', 'What', 'Description', 'Amount', 'Sub Account')

    def __init__(self, db):
        self.existence = []
        self.life = []
        self.db = db
        self.merged = self.db.get_merged()

        self.auto_existence_labeled = pd.DataFrame()
        self.un_labeled = pd.DataFrame()
        self.part_labeled = pd.DataFrame()

        self.labeled_data = pd.DataFrame(merged_types, index=[])
        self.labeled_data = self.labeled_data.astype(merged_types)

    def begin_classification(self):
        data = self.db.get_database()
        joined = data.merge(self.merged, how='outer', left_on=['ref'], right_on=['ref'], indicator=True)

        # labeled = joined[joined['_merge'] == 'both'].drop('_merge', axis=1)

        un_labeled = joined[joined['_merge'] == 'left_only'].dropna(axis=1, how='all')
        if un_labeled.empty:
            return None

        un_labeled = un_labeled.drop('_merge', axis=1)

        un_labeled = un_labeled.rename(columns={'Description_x': 'Description'})

        auto_existence_labeled, un_labeled = self.classify_existence_certain(un_labeled)
        self.auto_existence_labeled = auto_existence_labeled
        self.un_labeled = un_labeled

        self.setup_for_manual_classification()

    @staticmethod
    def classify_existence_certain(data: pd.DataFrame):
        with open('classification_data/certain_existence.json') as file:
            existence_keys = json.load(file)

        labeled_data = pd.DataFrame(merged_types, index=[])
        labeled_data = labeled_data.astype(merged_types)

        for who, keys in existence_keys.items():
            print(data)
            identified = data[data['Description'].str.contains('|'.join(keys))]
            if len(identified):
                labeled = pd.DataFrame({
                    'ref': identified['ref'].reset_index(drop=True),
                    'Who': pd.Series(who, index=range(len(identified))),
                    'What': pd.Series('', index=range(len(identified))),
                    'Description': pd.Series('', index=range(len(identified))),
                    'Amount': identified['Value'].reset_index(drop=True),
                    'Sub Account': pd.Series('existence', index=range(len(identified))),

                })
                labeled = labeled.astype(merged_types)
                labeled_data = pd.concat([labeled_data, labeled], ignore_index=True)

        # remove double classified data
        dups = labeled_data.duplicated(subset=['ref'])
        duplicated_rows = labeled_data[labeled_data['ref'].isin(labeled_data[dups]['ref'])]
        labeled_data = labeled_data.drop(index=duplicated_rows.index)

        # remove labeled rows from un labeled data
        data = data.drop(index=data[data['ref'].isin(labeled_data['ref'])].index)

        return labeled_data, data

    def setup_for_manual_classification(self):
        with open('classification_data/life.json') as file:
            life_keys = json.load(file)

        part_labeled = pd.DataFrame(merged_types, index=[])
        part_labeled = part_labeled.astype(merged_types)

        for who, keys in life_keys.items():
            if not keys:
                continue
            identified = self.un_labeled[self.un_labeled['Description'].str.contains('|'.join(keys))]
            if len(identified):
                labeled = pd.DataFrame({
                    'ref': identified['ref'].reset_index(drop=True),
                    'Who': pd.Series(who, index=range(len(identified))),
                    'What': pd.Series('', index=range(len(identified))),
                    'Description': pd.Series('', index=range(len(identified))),
                    'Amount': identified['Value'].reset_index(drop=True),
                    'Sub Account': pd.Series('life', index=range(len(identified))),

                })
                labeled = labeled.astype(merged_types)
                part_labeled = pd.concat([part_labeled, labeled], ignore_index=True)

        self.part_labeled = part_labeled

    def get_entry_prerequisites_for_manual_entry(self, index):
        row = self.un_labeled.iloc[index]
        part_labeled_row = self.part_labeled[self.part_labeled['ref'] == row['ref']]

        if not len(part_labeled_row):
            part_labeled_row = pd.DataFrame({
                'ref': [row['ref']],
                'Who': [''],
                'What': [''],
                'Description': [''],
                'Amount': [row['Value']],
                'Sub Account': ['existence'],

            })
        else:
            part_labeled_row = part_labeled_row.reset_index().iloc[0]  # extract the single row
            part_labeled_row = part_labeled_row.to_frame().T.drop('index',
                                                                  axis=1)  # and make it into a len 1 data frame
        mappings = {key: list(self.merged[key].value_counts().keys()) for key in ('Who', 'What', 'Sub Account')}
        return part_labeled_row, mappings

    @staticmethod
    def _process_category(mapping, entry, key):
        if entry is None:
            return None
        while True:
            try:
                return mapping[int(entry)]
            except ValueError:
                return entry
            except IndexError:
                entry = input(f'Category "{entry}" does not exist in {key} please re enter: ')

    @staticmethod
    def process_user_input(data, part_labeled_row: pd.DataFrame):

        user_input = list(map(lambda x: x.strip(), data))
        if any(map(lambda x: '|' in x, user_input)):
            user_inputs = list(map(lambda x: x.split('|'), user_input))
            user_inputs = [list(map(lambda y: y[key] if len(y) == 2 else y[0], user_inputs)) for key in
                           range(2)]
            print(user_inputs)
        else:
            user_inputs = [user_input]

        # convert user inputs to keyed data
        user_inputs = list(map(
            lambda user_entries: {key: None if value == '' else value for key, value in
                                  zip_longest(Classifier.expected_fields, user_entries)},
            user_inputs))

        try:
            amount_sum = sum(map(lambda x: float(x['Amount']), user_inputs))
            if amount_sum != part_labeled_row.at[0, 'Amount']:
                for i, entered_data in enumerate(user_inputs):
                    floaty = float(entered_data['Amount']) / amount_sum * part_labeled_row.at[0, 'Amount']
                    amount = (math.ceil(floaty * 100) if i % 2 else math.floor(floaty * 100)) / 100
                    user_inputs[i]['Amount'] = amount
        except ValueError:
            raise ValueError(f'Failed to convert Amounts to numeric value')
        except ZeroDivisionError:
            raise ZeroDivisionError('Bad ratio in Amount')

        for i, user_input in enumerate(user_inputs):
            for column in part_labeled_row.columns:
                if column not in user_input:
                    user_inputs[i][column] = part_labeled_row.at[0, column]
        return user_inputs

    def process_incoming_input(self, data):
        new_data = pd.DataFrame(data)
        new_data.astype(merged_types)
        self.labeled_data = pd.concat([self.labeled_data, new_data], ignore_index=True)
        self.labeled_data.to_csv('display_files/user_labeled_backup.csv')

    def classify_off_record(self):
        pass
