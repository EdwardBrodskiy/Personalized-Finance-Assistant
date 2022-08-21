from structures import mp

existence_keys = {
    'TVLICENSING.CO.UK': 'TV Licensing',
    'BRITISH GAS': 'British Gas',
    'LAMBETH': ' Council Tax',
    'THAMES WATER': 'Thames Water',
    'TRAVEL': 'Travel',
    'VPN': 'VPN',
}


class Classifier:
    def __init__(self):
        self.existence = []
        self.life = []

    def classify(self):
        pass
        # Identify concrete existence transactions

        # Identify concrete Life transactions

        # Label transactions

    def classify_row(self, row):
        for key, value in existence_keys.items():
            if key in row[mp['Description']]:
                self.existence.append((row[mp['Date']], value, float(row[mp['Value']])))
