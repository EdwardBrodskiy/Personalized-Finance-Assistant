import pandas as pd

'''
expanded here for ease of lookup

Special ops:
    ~ : Not operator which can be included in front of any other rule

List Selectors (Mostly for selecting based on tags):
    Any : takes a list returns True if any are found
    All : takes a list returns True if all are found

String Selectors (for columns like Description):
    Includes : takes a list returns True if any of the strings are contained within
    
Length selectors:
    Has : takes an integer returns equivalent of (x >= len(row_value)
'''


def rule_to_selector(rule_key, inputs):
    is_not = False
    if rule_key[0] == '~':
        is_not = True
        rule_key = rule_key[1:]

    selector = internal_map_to_selector(rule_key, inputs)
    if is_not:
        return lambda series: ~pd.Series(selector(series))
    return selector


def internal_map_to_selector(rule_key, inputs):
    if rule_key == 'Any':
        return lambda series: pd.Series(series).apply(lambda x: any(tag in x for tag in inputs))
    elif rule_key == 'All':
        return lambda series: pd.Series(series).apply(lambda x: all(tag in x for tag in inputs))
    elif rule_key == 'Has':
        return lambda series: pd.Series(series).apply(lambda x: len(x) <= inputs)
    elif rule_key == 'Includes':
        return lambda series: pd.Series(series).str.contains('|'.join(inputs))
    raise NotImplementedError(f'No selector called {rule_key}')


