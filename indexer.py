import csv
import logging
import os
import re
from collections import Counter

import numpy as np
import pandas as pd

from configuration import get_filepaths, get_transaction_formats
from helper_functions import ensure_dir_exists
from structures import database_types


def get_items_from_input():
    inputs_path = get_filepaths()['inputs']
    csv_formats = get_transaction_formats()['input data column format']
    database_columns = list(database_types.keys())
    ensure_dir_exists(inputs_path)
    all_rows = []
    for source in os.listdir(inputs_path):
        directory = os.path.join(inputs_path, source)
        if not os.path.isdir(directory):
            continue  # skip if not a directory

        # identify csv format
        directory_format = None
        for csv_format in csv_formats:
            if re.match(f'^{csv_format}.*', source):
                directory_format = csv_format
                break
        if directory_format is None:
            raise Exception(f'The directory "{source}" implies and undefined format. '
                            f'Defined formats are {csv_formats.keys()}')

        for filename in gather_all_years(directory):
            with open(os.path.join(directory, filename)) as file:
                reader = csv.reader(file)
                first_data_row_found = False
                for i, row in enumerate(reader):
                    if not row:  # skip empty row
                        continue
                    # check for header if a data row hasn't been seen yet
                    # (this reduces the chance that invalid data rows are not reported)
                    if not first_data_row_found:
                        # check if non string values are of the correct type
                        type_issue_found = False
                        type_casters = {'float64': float, 'int64': int, 'datetime64[ns]': pd.to_datetime}
                        for column in [c for c in csv_formats[directory_format] if
                                       database_types[c] in type_casters]:
                            expected_type = database_types[column]
                            value = row[csv_formats[directory_format].index(column)]
                            try:
                                type_casters[expected_type](value)
                            except (TypeError, ValueError) as e:
                                # this means this must be the header row
                                type_issue_found = True
                                break
                        if type_issue_found:
                            continue
                        first_data_row_found = True  # passed all the checks so is likely to be a data row

                    # match and strip commas in numerical columns
                    for column in [c for c in csv_formats[directory_format]]:
                        expected_type = database_types[column]
                        if expected_type in ('float64', 'int64'):
                            value_index = csv_formats[directory_format].index("Value")
                            regex = re.compile(',')  # matches a comma
                            row[value_index] = regex.sub('', row[value_index])

                    # add row

                    # pYtHoNiC
                    mapping = {
                        csv_formats[directory_format].index(inputs_csv_column): list(database_types.keys()).index(
                            database_column) for inputs_csv_column in csv_formats[directory_format] for database_column
                        in database_types if inputs_csv_column == database_column
                    }

                    # Sane individual
                    mapping = {}
                    csv_columns = csv_formats[directory_format]
                    for inputs_csv_column in csv_formats[directory_format]:
                        for database_column in database_types:
                            if inputs_csv_column == database_column:
                                mapping[csv_columns.index(inputs_csv_column)] = database_columns.index(database_column)

                    empty_row = [np.nan for _ in database_types]
                    empty_row[database_columns.index('Source')] = source
                    for input_col, database_column in mapping.items():
                        empty_row[database_column] = row[input_col]
                    all_rows.append(empty_row)

    items_table = pd.DataFrame(data=all_rows, columns=database_columns)

    for dated_column in [column for column, expected_type in database_types.items() if
                         expected_type == 'datetime64[ns]']:
        items_table[dated_column] = pd.to_datetime(items_table[dated_column], dayfirst=True)
    items_table['ref'] = items_table.index

    items_table = items_table.astype(database_types)

    items_table = items_table.replace(r'^\s*$', np.nan, regex=True)
    items_table.index.name = 'key'
    return items_table


def gather_all_years(directory):
    # get all file names in the directory
    files = os.listdir(directory)
    # filter for files that end with '.csv' and start with a 4-digit number
    year_files = [f for f in files if f.endswith('.csv') and f[:4].isdigit() and len(f) == 8]
    if year_files:
        return list(sorted(year_files))
    elif 'full.csv' in files:
        return ['full.csv', ]
    return []


def find_new(possibly_new, existing):
    combined_key = ['Date', 'Value', 'Balance', 'Source']
    df1 = possibly_new[combined_key]
    df2 = existing[combined_key]

    # Convert each row in the dataframes to a tuple and count the occurrences of each tuple
    counter_df1 = Counter(df1.apply(lambda row: TupleWithAKey(row, key=row.name), axis=1))
    counter_df2 = Counter(df2.apply(lambda row: TupleWithAKey(row, key=row.name), axis=1))

    # Subtract the counts in df2 from the counts in df1
    counter_diff = counter_df1 - counter_df2

    new = possibly_new.loc[map(lambda x: x.key, counter_diff.elements())]
    return new


class TupleWithAKey:
    def __init__(self, array, key=None):
        self.key = key
        self.array = tuple(array)

    def __eq__(self, other):
        if type(other) is TupleWithAKey:
            return self.array == other.array
        raise NotImplementedError()

    def __hash__(self):
        return hash(self.array)


def index(db):
    incoming_table = get_items_from_input()
    current_table = db.get_database()

    new = find_new(incoming_table, current_table)

    logging.info(f'\nFound these new entries:\n{new}')

    db.add_to_database(new)

    return new  # return intended for info based output only
