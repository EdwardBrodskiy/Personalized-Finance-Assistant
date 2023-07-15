import csv
import logging
import os
import re
from collections import Counter

import numpy as np
import pandas as pd

from configuration import get_filepaths, get_transaction_formats, get_best_default
from helper_functions import ensure_dir_exists
from structures import database_types


def get_items_from_input():
    inputs_path = get_filepaths()['inputs']
    database_columns = list(database_types.keys())
    ensure_dir_exists(inputs_path)

    items_table = pd.DataFrame(columns=database_columns)

    for source in os.listdir(inputs_path):
        rows = []
        sort_key = get_best_default(source, 'SortBy')
        is_day_first = get_best_default(source, 'dayFirst')
        is_day_first = True if is_day_first is None else is_day_first  # day/month/year if none specified

        populate_rows_from_source(rows, source)

        incoming_rows = pd.DataFrame(data=rows, columns=database_columns)

        dated_columns = [
            column
            for column, expected_type
            in database_types.items()
            if expected_type == 'datetime64[ns]'
        ]
        for dated_column in dated_columns:
            incoming_rows[dated_column] = pd.to_datetime(incoming_rows[dated_column], dayfirst=is_day_first)

        if sort_key is not None and sort_key in incoming_rows.columns:
            incoming_rows = incoming_rows.sort_values(by=sort_key)
        print(incoming_rows)

        for column in incoming_rows.columns:
            default_value = get_best_default(source, column)
            if default_value is not None:
                incoming_rows[column] = incoming_rows[column].fillna(default_value)

        items_table = pd.concat([items_table, incoming_rows], ignore_index=True)

    items_table['ref'] = items_table.index

    items_table = items_table.astype(database_types)

    items_table = items_table.replace(r'^\s*$', np.nan, regex=True)
    items_table.index.name = 'key'
    return items_table


def populate_rows_from_source(rows, source):
    inputs_path = get_filepaths()['inputs']
    csv_formats = get_transaction_formats()['input data column format']
    database_columns = list(database_types.keys())

    directory = os.path.join(inputs_path, source)
    if not os.path.isdir(directory):
        return  # skip if not a directory

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
            csv_rows = list(csv.reader(file))

        first_data_row_found = False
        for row in csv_rows:
            if not row:  # skip empty row
                continue
            # check for header if a data row hasn't been seen yet
            # (this reduces the chance that invalid data rows are not reported)
            if not first_data_row_found:
                first_data_row_found = is_data_row(row, directory_format)
                if not first_data_row_found:
                    continue

            clean_numerical_columns(row, directory_format)

            # add row
            database_row = [np.nan for _ in database_types]
            database_row[database_columns.index('Source')] = source

            map_to_database_row(row, database_row, directory_format)
            rows.append(database_row)


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


def is_data_row(row, directory_format):
    csv_formats = get_transaction_formats()['input data column format']
    csv_column_names = csv_formats[directory_format]
    # check if non string values are of the correct type
    type_casters = {'float64': float, 'int64': int, 'datetime64[ns]': lambda x: pd.to_datetime(x, dayfirst=True)}
    for column_name in [c for c in csv_column_names if
                        database_types[c] in type_casters]:
        expected_type = database_types[column_name]
        value = row[csv_column_names.index(column_name)]
        try:
            type_casters[expected_type](value)
        except (TypeError, ValueError):
            # this means this must be the header row
            return False

    return True


def map_to_database_row(row, database_row, directory_format):
    csv_formats = get_transaction_formats()['input data column format']
    csv_column_names = csv_formats[directory_format]
    database_columns = list(database_types.keys())

    mapping = {}
    for inputs_csv_column in csv_column_names:
        for database_column in database_types:
            if inputs_csv_column != database_column:
                continue
            csv_column_index = csv_column_names.index(inputs_csv_column)
            database_column_index = database_columns.index(database_column)
            mapping[csv_column_index] = database_column_index

    for input_col, database_column in mapping.items():
        database_row[database_column] = row[input_col]


def clean_numerical_columns(row, directory_format):
    csv_formats = get_transaction_formats()['input data column format']
    csv_column_names = csv_formats[directory_format]
    # match and strip commas in numerical columns
    for column_name in csv_column_names:
        expected_type = database_types[column_name]
        if expected_type in ('float64', 'int64'):
            value_index = csv_column_names.index(column_name)
            regex = re.compile(',')  # matches a comma
            row[value_index] = regex.sub('', row[value_index])


def find_new(possibly_new, existing):
    combined_key = ['Date', 'Value', 'Balance', 'Source']
    # cast to string and replace nan as nan == nan is False
    df1 = possibly_new[combined_key].astype('string').fillna('<empty>')
    df2 = existing[combined_key].astype('string').fillna('<empty>')

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

    def __repr__(self):
        return repr(self.array)


def index(db):
    incoming_table = get_items_from_input()
    current_table = db.get_database()

    new = find_new(incoming_table, current_table)

    logging.info(f'\nFound these new entries:\n{new}')

    db.add_to_database(new)

    return new  # return intended for info based output only
