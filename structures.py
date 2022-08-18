import numpy as np

mp = {'Date': 0, 'Type': 1, 'Description': 2, 'Value': 3, 'Balance': 4, 'Account Name': 5, 'Account Number': 6}
database_types = {'Date': np.datetime64, 'Type': 'category', 'Description': 'string', 'Value': np.float64, 'Balance': np.float64,
                  'Account Name': 'string',
                  'Account Number': 'string'}
