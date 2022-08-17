import csv
import pandas as pd
import numpy as np
from structures import mp



existence_keys = {
    'TVLICENSING.CO.UK': 'TV Licensing',
    'BRITISH GAS': 'British Gas',
    'LAMBETH': ' Council Tax',
    'THAMES WATER': 'Thames Water',
    'TRAVEL': 'Travel',
    'VPN': 'VPN',
}




def main():
    classifier = Classifier()
    for year in range(2019, 2023):
        with open(f'input/{year}.csv') as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row) == len(mp) + 1:
                    classifier.classify_row(row)

    existence = pd.DataFrame(data=classifier.existence, columns=['Date', 'Who', 'Amount'])
    existence.astype({'Date': str, 'Who': 'category', 'Amount': np.float64})

    print(existence.groupby(['Who']).sum())

    print(existence['Amount'].sum())


class Classifier:
    def __init__(self):
        self.existence = []
        self.life = []

    def classify_row(self, row):
        for key, value in existence_keys.items():
            if key in row[mp['Description']]:
                self.existence.append((row[mp['Date']], value, float(row[mp['Value']])))


if __name__ == '__main__':
    main()
