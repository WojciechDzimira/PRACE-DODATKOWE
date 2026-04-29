import pandas as pd

def assign_period(date):
    if date < pd.Timestamp(2024, 6, 1): return "1. Początek"
    if date < pd.Timestamp(2024, 10, 1): return "2. Dane zakłamane"
    if date < pd.Timestamp(2025, 12, 1): return "3. Wzrost"
    return "4. Najnowsze"

def get_range(row):
    start_date = row['Data transakcji']
    plan = row['Czas dostępu']
    
    months_count = {
        'Miesiąc': 1,
        'Rok': 12,
        '2 Lata': 24
    }.get(plan, 1)
    
    start_period = start_date.to_period('M')
    return [start_period + i for i in range(months_count)]

def check_if_returned(row):
    active = row[row == 1].index
    if len(active) < 2: return 0 
    if 0 in row.loc[active[0]:active[-1]].values:
        return 1
    return 0

def subscription_time(row):
    offsets = {
        'Miesiąc': pd.DateOffset(months=1),
        'Rok':     pd.DateOffset(years=1),
        '2 Lata':  pd.DateOffset(years=2)}
    offset = offsets.get(row['Czas dostępu'])

    return row['Data transakcji'] + offset if offset else row['Data transakcji']


def get_trend(f, l, n):
    if n == 1: return 'Stabilne'
    if l > f:  return 'Upgrade'
    if l < f:  return 'Downgrade' 
    return 'Mieszany' 