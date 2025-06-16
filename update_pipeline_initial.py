import pandas as pd
from datetime import datetime

# Load the dataframes
df_new = pd.read_csv("purchase_items(8).csv")
df_old = pd.read_excel("Open_purchase_order_items_June_3rd(1).xlsx", engine='openpyxl')

# Define merge keys
merge_keys = ["Purchase Order", "SKU"]

# Print initial shapes for verification
print(f"Original new data shape: {df_new.shape}")
print(f"Original old data shape: {df_old.shape}")

# First rename 'Ready' to 'ETD' in old dataframe if it exists
if 'Ready' in df_old.columns:
    df_old = df_old.rename(columns={'Ready': 'ETD'})

# 1. Identify records that exist in both dataframes
common_records = pd.merge(
    df_old[merge_keys], 
    df_new[merge_keys],
    on=merge_keys,
    how='inner'
)

# 2. Identify records that only exist in the new dataframe and create a proper copy
new_only_records = df_new[~df_new.set_index(merge_keys).index.isin(
    common_records.set_index(merge_keys).index
)].copy()  # Create explicit copy

# 3. Create the final merged dataframe
# First, get the matching records from old dataframe (preserving ALL their data)
preserved_old = df_old[df_old.set_index(merge_keys).index.isin(
    common_records.set_index(merge_keys).index
)]

# Initialize ETD and Comment columns in new_only_records using loc
new_only_records.loc[:, 'ETD'] = ''
new_only_records.loc[:, 'Comment'] = ''

# Ensure new_only_records has the same columns as preserved_old
missing_cols = set(preserved_old.columns) - set(new_only_records.columns)
for col in missing_cols:
    new_only_records.loc[:, col] = ''

# Combine preserved old records with new-only records
df_merged = pd.concat([preserved_old, new_only_records[preserved_old.columns]], ignore_index=True)

# Add Customer Order column if not already present
if 'Customer Order' not in df_merged.columns:
    df_merged['Customer Order'] = ''

# Convert date columns
date_columns = ['PO Date', 'ETD']
for col in date_columns:
    if col in df_merged.columns:
        df_merged[col] = pd.to_datetime(df_merged[col], format='%d/%m/%Y', errors='coerce')

# Print verification information
print("\nMerge Results:")
print(f"Final merged shape: {df_merged.shape}")
print(f"Records preserved from old file: {len(preserved_old)}")
print(f"New records added: {len(new_only_records)}")

# Save the result
df_merged.to_csv("updated_order_list.csv", index=False)

# Print sample of merged data
print("\nSample of preserved records (from old file):")
print(preserved_old[merge_keys + ['ETD', 'Comment'] if 'ETD' in preserved_old.columns else merge_keys].head())
print("\nSample of new records:")
print(new_only_records[merge_keys].head())