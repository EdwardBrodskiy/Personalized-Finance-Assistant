from structures import merged_types
import json
import pandas as pd
from database import DataBase


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

        labeled_data = pd.DataFrame(merged_types, index=[])
        labeled_data = labeled_data.astype(merged_types)

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
                labeled_data = pd.concat([labeled_data, labeled], ignore_index=True)

        data = data.drop(index=data[data['ref'].isin(labeled_data['ref'])].index)
        print(data.head(60))

        return labeled_data, data


def main():
    cl = Classifier()
    db = DataBase()
    data = db.get_database()
    merged = db.get_merged()
    print(merged[merged['Sub Account'] == 'life']['Who'].value_counts())
    joined = data.merge(merged, how='outer', left_on=['ref'], right_on=['ref'], indicator=True)

    good = joined[joined['_merge'] == 'both'].drop('_merge', axis=1)

    un_labeled = joined[joined['_merge'] == 'left_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

    un_labeled = un_labeled.rename(columns={'Description_x': 'Description'})
    print(un_labeled.info())
    existence_labeled, un_labeled = cl.classify_existence_certain(un_labeled)
    life_labeled, un_labeled = cl.classify_life(un_labeled)
    db.add_to_merged(existence_labeled)



if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    main()
