from structures import merged_types, database_types
import json
import pandas as pd
from database import DataBase
from itertools import zip_longest


class Classifier:
    def __init__(self):
        self.existence = []
        self.life = []

    def classify(self):
        pass
        # Identify concrete existence transactions

        # Identify concrete Life transactions

        # Label transactions

    #
    # def classify_row(self, row):
    #     for key, value in existence_keys.items():
    #         if key in row[mp['Description']]:
    #             self.existence.append((row[mp['Date']], value, float(row[mp['Value']])))

    def classify_existence_certain(self, data: pd.DataFrame):
        with open('classification_data/certain_existence.json') as file:
            existence_keys = json.load(file)

        labeled_data = pd.DataFrame(merged_types, index=[])
        labeled_data = labeled_data.astype(merged_types)

        for who, keys in existence_keys.items():
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

        data = data.drop(index=data[data['ref'].isin(labeled_data['ref'])].index)

        return labeled_data, data

    def classify_life(self, data: pd.DataFrame):
        with open('classification_data/life.json') as file:
            life_keys = json.load(file)

        part_labeled = pd.DataFrame(merged_types, index=[])
        part_labeled = part_labeled.astype(merged_types)

        for who, keys in life_keys.items():
            if not keys:
                continue
            identified = data[data['Description'].str.contains('|'.join(keys))]
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

        labeled_data, data = self._manual_entry(data, part_labeled)

        data = data.drop(index=data[data['ref'].isin(part_labeled['ref'])].index)

        return part_labeled, data

    def _manual_entry(self, data, part_labeled):
        db = DataBase()
        merged = db.get_merged()

        labeled_data = pd.DataFrame(merged_types, index=[])
        labeled_data = labeled_data.astype(merged_types)

        data = data.sort_values('Date')

        # get categories used and map them to a number (index)
        mappings = {key: list(merged[key].value_counts().keys()) for key in ('Who', 'What', 'Sub Account')}

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
                part_labeled_row = part_labeled_row.to_frame().T.drop('index', axis=1) # and make it into a len 1 data frame
            part_labeled_row = part_labeled_row.astype(merged_types)

            # User information display

            chars_wide = 140
            print('#' * chars_wide)

            print(f'Part Labeled row:\n{part_labeled_row}')

            for key, mapping in mappings.items():
                if key in expected_fields:

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
                    user_inputs = [list(map(lambda y: y[key] if len(y) == 2 else y[0], user_inputs)) for key in range(2)]
                    print(user_inputs)
                else:
                    user_inputs = [user_input]

                for user_entries in user_inputs:
                    entered_data = {key: None if value == '' else value for key, value in zip_longest(expected_fields, user_entries)}
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
                                row_to_label.at[0,key] = float(value)
                            except:
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
                print(f'\nCurrently labeled data:\n{labeled_data}')
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



def main():
    cl = Classifier()
    db = DataBase()
    data = db.get_database()
    merged = db.get_merged()
    joined = data.merge(merged, how='outer', left_on=['ref'], right_on=['ref'], indicator=True)

    good = joined[joined['_merge'] == 'both'].drop('_merge', axis=1)

    un_labeled = joined[joined['_merge'] == 'left_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

    un_labeled = un_labeled.rename(columns={'Description_x': 'Description'})

    existence_labeled, un_labeled = cl.classify_existence_certain(un_labeled)
    life_labeled, un_labeled = cl.classify_life(un_labeled)
    db.add_to_merged(existence_labeled)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    main()
