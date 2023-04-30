from structures import merged_types, database_types
import json
import pandas as pd
from itertools import zip_longest
import math


class Classifier:
    def __init__(self, db):
        self.existence = []
        self.life = []
        self.db = db
        self.merged = self.db.get_merged()

        self.auto_existence_labeled = pd.DataFrame()
        self.un_labeled = pd.DataFrame()
        self.part_labeled = pd.DataFrame()

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

    def _manual_entry(self, data, part_labeled):

        data.merge(part_labeled, left_on=['ref'], right_on=['ref'], how='outer').to_csv(
            'display_files/manual_entry_data.csv')

        labeled_data = pd.DataFrame(merged_types, index=[])
        labeled_data = labeled_data.astype(merged_types)

        data = data.sort_values('Date')

        # get categories used and map them to a number (index)
        mappings = {key: list(self.merged[key].value_counts().keys()) for key in ('Who', 'What', 'Sub Account')}

        for index, row in data.iterrows():
            part_labeled_row = part_labeled[part_labeled['ref'] == row['ref']]

            # work out what information we need from user
            if not len(part_labeled_row):
                part_labeled_row = pd.DataFrame({
                    'ref': [row['ref']],
                    'Who': [''],
                    'What': [''],
                    'Description': [''],
                    'Amount': [row['Value']],
                    'Sub Account': ['existence'],

                })

                expected_fields = ['Who', 'What', 'Description', 'Sub Account', 'Amount']
            else:
                expected_fields = ['What', 'Description', 'Sub Account', 'Amount']
                part_labeled_row = part_labeled_row.reset_index().iloc[0]  # extract the single row
                part_labeled_row = part_labeled_row.to_frame().T.drop('index',
                                                                      axis=1)  # and make it into a len 1 data frame
            part_labeled_row = part_labeled_row.astype(merged_types)

            # User information display

            chars_wide = 140
            print('#' * chars_wide)

            print(f'Part Labeled row:\n{part_labeled_row}')

            for key, mapping in mappings.items():

                text_pairs = [f'{value}  {i}' for i, value in enumerate(mapping)]
                max_length = max(map(len, text_pairs))
                text_pairs = list(map(lambda x: x.ljust(max_length + 2), text_pairs))

                display_columns = chars_wide // max_length
                display_rows = len(text_pairs) // display_columns + 1

                print(f'\nCategories for {key}:\n')
                for i in range(display_rows):
                    print('|'.join(text_pairs[i * display_columns: (i + 1) * display_columns]))

            print(f'\nIncoming data to be labeled:\n{row.to_frame().T}')
            user_input = input(f'Enter {", ".join(expected_fields)}\n>>>')
            if user_input == 'finish':
                break
            elif user_input in ['exit', 'cancel']:
                exit()
            elif user_input in ['s', 'skip', '']:
                continue
            else:
                user_input = list(map(lambda x: x.strip(), user_input.split(',')))
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
                                          zip_longest(expected_fields, user_entries)},
                    user_inputs))

                try:
                    if user_inputs[0]['Amount'] is not None:
                        amount_sum = sum(map(lambda x: float(x['Amount']), user_inputs))
                        if amount_sum != part_labeled_row.at[0, 'Amount']:
                            for i, entered_data in enumerate(user_inputs):
                                floaty = float(entered_data['Amount']) / amount_sum * part_labeled_row.at[0, 'Amount']
                                amount = (math.ceil(floaty * 100) if i % 2 else math.floor(floaty * 100)) / 100
                                user_inputs[i]['Amount'] = amount
                except ValueError:
                    print(f'Failed to convert Amounts to float skipping')
                    continue
                except ZeroDivisionError:
                    print('bad ratio on Amount skipping')
                    continue

                for entered_data in user_inputs:
                    row_to_label = part_labeled_row.copy(deep=True)

                    # convert number shortcut to full category name
                    for key, mapping in mappings.items():
                        if key in expected_fields:
                            entered_data[key] = self._process_category(mapping, entered_data[key], key)

                            if entered_data[key] not in mapping:
                                mappings[key].append(entered_data[key])

                    for key, value in entered_data.items():
                        if value is None:
                            continue
                        if key == 'Amount':
                            try:
                                row_to_label.at[0, key] = float(value)
                            except ValueError:
                                print(f'Failed to convert {value} to float skipping')
                                break
                        elif key in ['Who', 'What']:
                            row_to_label[key] = row_to_label[key].cat.add_categories(value)
                            row_to_label.at[0, key] = value
                        else:
                            row_to_label.at[0, key] = value
                    else:
                        print(f'\nAdding row: +++++\n{row_to_label}')
                        labeled_data = pd.concat([labeled_data, row_to_label], ignore_index=True)
                labeled_data.to_csv('display_files/user_labeled_backup.csv')
                print(f'\nCurrently labeled data:\n{labeled_data}')
        entry = 'indexes to delete'
        while entry:
            print(labeled_data.tail(60))
            entry = input('Do you want to delete any?\n')
            if entry:
                to_delete = list(map(lambda x: int(x), entry.split(',')))
                labeled_data = labeled_data.drop(index=to_delete)

        return labeled_data, data

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
        expected_fields = ['Who', 'What', 'Description', 'Sub Account', 'Amount']
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
                                  zip_longest(expected_fields, user_entries)},
            user_inputs))

        try:
            amount_sum = sum(map(lambda x: float(x['Amount']), user_inputs))
            if amount_sum != part_labeled_row.at[0, 'Amount']:
                for i, entered_data in enumerate(user_inputs):
                    floaty = float(entered_data['Amount']) / amount_sum * part_labeled_row.at[0, 'Amount']
                    amount = (math.ceil(floaty * 100) if i % 2 else math.floor(floaty * 100)) / 100
                    user_inputs[i]['Amount'] = amount
        except ValueError:
            raise ValueError(f'Failed to convert Amounts to float skipping')

        except ZeroDivisionError:
            raise ZeroDivisionError('bad ratio on Amount skipping')
        return user_inputs

    def classify_off_record(self):
        pass
