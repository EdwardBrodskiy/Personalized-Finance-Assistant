import logging

import numpy as np

from configuration import get_transaction_formats


additional_database_types = {'Source': 'category', "ref": "int64"}
user_database_definition = get_transaction_formats()['DataBaseTypes']
for column in user_database_definition:
    if column in additional_database_types:
        logging.warning(f'User defined type "{column}" collides with internal database types. '
                        f'Please change the column name')

database_types = user_database_definition | additional_database_types

merged_types = {
    'ref': np.int64,
    'Tags': 'object',
    'Description': 'string',
    'Amount': np.float64,
}

off_record_types = {
    'ref': np.int64,
    'Date': 'datetime64[ns]',
    'Who': 'category',
    'What': 'category',
    'Description': 'string',
    'Amount': np.float64,
    'Sub Account': 'string'
}
