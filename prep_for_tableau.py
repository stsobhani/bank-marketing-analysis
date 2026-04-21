import pandas as pd

# Load the real dataset
df = pd.read_csv(
    r'C:\Users\shaya\Documents\SQL\bank-additional\bank-additional-full.csv',
    sep=';'
)

print(f"Loaded {len(df):,} records, {len(df.columns)} columns")

# Rename columns (no dots, no reserved words)
df = df.rename(columns={
    'default':        'credit_default',
    'emp.var.rate':   'emp_var_rate',
    'cons.price.idx': 'cons_price_idx',
    'cons.conf.idx':  'cons_conf_idx',
    'nr.employed':    'nr_employed',
})

# Add helper columns so Tableau doesn't need formulas
# Subscribed as 0/1 number (for AVG = response rate)
df['subscribed_num'] = (
    df['y'].astype(str).str.strip().str.lower() == 'yes'
).astype(int)
print(df['subscribed_num'].value_counts())

# Age band
def age_band(age):
    if age < 25:   return '18-24'
    elif age < 35: return '25-34'
    elif age < 45: return '35-44'
    elif age < 55: return '45-54'
    elif age < 65: return '55-64'
    else:          return '65+'
df['age_band'] = df['age'].apply(age_band)

# Education ordinal label (for sorting)
edu_order = {
    'illiterate': '1_illiterate',
    'basic.4y':   '2_basic_4y',
    'basic.6y':   '3_basic_6y',
    'basic.9y':   '4_basic_9y',
    'high.school':'5_high_school',
    'professional.course': '6_professional',
    'university.degree':   '7_university',
    'unknown':    '8_unknown',
}
df['education_ranked'] = df['education'].map(edu_order)

# Campaign contact bucket
def campaign_bucket(n):
    if n == 1:       return '1 contact'
    elif n == 2:     return '2 contacts'
    elif n == 3:     return '3 contacts'
    elif n <= 5:     return '4-5 contacts'
    else:            return '6+ contacts'
df['campaign_bucket'] = df['campaign'].apply(campaign_bucket)

# Previously contacted flag
df['prev_contacted'] = df['pdays'].apply(lambda x: 'Previously contacted' if x != 999 else 'First-time contact')

# Month sort order (so charts show Jan to Dec and not alphabetical)
month_order = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
               'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
df['month_num'] = df['month'].map(month_order)

# Euribor band
def euribor_band(r):
    if r < 1.5:   return 'Low (<1.5%)'
    elif r < 3.5: return 'Medium (1.5-3.5%)'
    else:         return 'High (>3.5%)'
df['euribor_band'] = df['euribor3m'].apply(euribor_band)

# Save as clean comma CSV
out_path = r'C:\Users\shaya\Documents\SQL\bank_for_tableau.csv'
df.to_csv(out_path, index=False)

print(f"\nSaved to: {out_path}")
print(f"Columns in output ({len(df.columns)}):")
for c in df.columns:
    print(f"  {c}")
print(f"\nReady to open in Tableau Public.")