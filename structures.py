import numpy as np

mp = {'Date': 0, 'Type': 1, 'Description': 2, 'Value': 3, 'Balance': 4, 'Account Name': 5, 'Account Number': 6}

database_types = {
    'Date': 'datetime64[ns]',
    'Type': 'category',
    'Description': 'string',
    'Value': np.float64,
    'Balance': np.float64,
    'Account Name': 'string',
    'Account Number': 'string',
    'ref': np.int64
}

merged_types = {
    'ref': np.int64,
    'Who': 'category',
    'What': 'category',
    'Description': 'string',
    'Amount': np.float64,
    'Sub Account': 'string'
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
