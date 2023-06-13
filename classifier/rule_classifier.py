import json
import math
import os
from itertools import zip_longest

import pandas as pd

from classifier.tag_rules_parser import rule_to_selector
from structures import merged_types
from web_app.helper_functions import extract_tags


class Classifier:
    expected_fields = ('ref', 'Description', 'Amount', 'Tags')

    def __init__(self, db):
        self.existence = []
        self.life = []
        self.db = db
        self.merged = self.db.get_merged()

        self.un_labeled = pd.DataFrame()
        self.part_labeled = pd.DataFrame()
        self.automatically_labeled = pd.DataFrame()

        self.labeled_data = pd.DataFrame(merged_types, index=[])
        self.labeled_data = self.labeled_data.astype(merged_types)

    def begin_classification(self):
        data = self.db.get_database()
        joined = data.merge(self.merged, how='outer', left_on=['ref'], right_on=['ref'], indicator=True)

        # labeled = joined[joined['_merge'] == 'both'].drop('_merge', axis=1)

        un_labeled = joined[joined['_merge'] == 'left_only']  # .dropna(axis=1, how='all')
        if un_labeled.empty:
            return None

        # for the purposes of tagging use the bank description
        un_labeled = un_labeled.rename(columns={'Description_x': 'Description'})
        un_labeled['Tags'] = un_labeled['Tags'].apply(lambda x: x if isinstance(x, list) else [])
        un_labeled['Description_y'] = un_labeled['Description_y'].fillna('')

        with open(os.path.join('classification_data', 'tag_rules.json')) as file:
            tag_rules = json.load(file)

        tagged_data = self._tag_data_based_on_rules(tag_rules, un_labeled)

        tagged_data['Amount'] = tagged_data['Value']
        # for merged switch back and don't use the bank description
        tagged_data = tagged_data.rename(
            columns={'Description': 'Description_x', 'Description_y': 'Description'})

        # extract and reformat automatically labeled data
        self.automatically_labeled = tagged_data[tagged_data['Tags'].apply(lambda x: 'Automatic' in x)]
        self.automatically_labeled = self.automatically_labeled[merged_types.keys()]

        self.un_labeled = tagged_data[tagged_data['Tags'].apply(lambda x: 'Automatic' not in x)]

        self.part_labeled = self.un_labeled[list(merged_types.keys())]

    @staticmethod
    def classify_existence_certain(data: pd.DataFrame):
        with open('./classification_data/certain_existence.json') as file:
            existence_keys = json.load(file)

        labeled_data = pd.DataFrame(merged_types, index=[])
        labeled_data = labeled_data.astype(merged_types)

        for who, keys in existence_keys.items():
            print(data.columns)
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
        # TODO: work out if this is important
        dups = labeled_data.duplicated(subset=['ref'])
        duplicated_rows = labeled_data[labeled_data['ref'].isin(labeled_data[dups]['ref'])]
        labeled_data = labeled_data.drop(index=duplicated_rows.index)

        # remove labeled rows from un labeled data
        data = data.drop(index=data[data['ref'].isin(labeled_data['ref'])].index)

        return labeled_data, data

    @staticmethod
    def _tag_data_based_on_rules(tag_rules, data: pd.DataFrame):
        for tag_rules_level in tag_rules:
            for tag, columns in tag_rules_level.items():
                for column, rules in columns.items():
                    prev_selector = None
                    for rule_key, inputs in rules.items():
                        selector = rule_to_selector(rule_key, inputs)(data[column])
                        if prev_selector is not None:
                            selector = prev_selector & selector
                        prev_selector = selector
                    data.loc[selector, 'Tags'] = data.loc[selector, 'Tags'].apply(
                        lambda x: x + [tag] if type(x) is list else [tag])

        return data

    def get_entry_prerequisites_for_manual_entry(self, index):
        row = self.un_labeled.iloc[index]
        row = pd.DataFrame(row).T.reset_index()
        # extract tags in common order in the relative scope of manual labeling
        non_automatically_labeled_rows = self.merged[self.merged['Tags'].apply(lambda x: 'Automatic' not in x)]
        tags = extract_tags(non_automatically_labeled_rows['Tags'])
        return row, {'Tags': tags}

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
        ref, *string_entries, tags = data

        split_tags = [[], []]
        for tag, assignment in tags:
            if assignment == 0:
                split_tags[0].append(tag)
                split_tags[1].append(tag)
            else:
                split_tags[assignment - 1].append(tag)
        split_tags = list(set(map(tuple, split_tags)))

        string_entries = list(map(str.strip, string_entries))
        # if either entry has split key character or two non-empty tag groups exist
        if any(map(lambda x: '|' in x, string_entries)) or len(split_tags) > 1:
            string_entries = list(map(lambda x: x.split('|'), string_entries))
            string_entries = [list(map(lambda y: y[key] if len(y) == 2 else y[0], string_entries)) for key in range(2)]
        else:
            string_entries = [string_entries]

        user_inputs = [{
            'ref': ref,
            'Description': str_entries[0] if string_entries is not None else None,
            'Amount': str_entries[1] if string_entries is not None else None,
            'Tags': tag
        } for str_entries, tag in zip_longest(string_entries, split_tags)]

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
            for column in merged_types.keys():
                if column not in user_input:
                    user_inputs[i][column] = part_labeled_row.at[0, column]
        return user_inputs

    def process_incoming_input(self, data):
        new_data = pd.DataFrame(data)
        new_data.astype(merged_types)
        self.labeled_data = pd.concat([self.labeled_data, new_data], ignore_index=True)
        self.labeled_data.to_csv(os.path.join('display_files', 'user_labeled_backup.csv'))

    def classify_off_record(self):
        pass
