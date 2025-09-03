import pandas as pd
from datetime import datetime

# Load the dataframes
df_new = pd.read_csv("purchase_items(39).csv")
df_old = pd.read_csv("updated_order_list.csv")

# Define merge keys and columns to keep
merge_keys = ["Purchase Order", "SKU"]
columns_to_keep = [
    "Purchase Order", "Product", "Variant", "SKU", 
    "PO Date", "Quantity", "ETD", "Comment", "Customer Order"
]

# Print initial shapes for verification
print(f"Original new data shape: {df_new.shape}")
print(f"Original old data shape: {df_old.shape}")

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
)].copy()

# 3. Create the final merged dataframe
# First, get the matching records from old dataframe (preserving ALL their data)
preserved_old = df_old[df_old.set_index(merge_keys).index.isin(
    common_records.set_index(merge_keys).index
)]

# Initialize ETD, Comment, and Customer Order columns in new_only_records
new_only_records['ETD'] = ''
new_only_records['Comment'] = ''
new_only_records.loc[:, 'Customer Order'] = ''

# Select only the columns we want to keep
preserved_old = preserved_old[columns_to_keep]
new_only_records = new_only_records[columns_to_keep]

# Combine preserved old records with new-only records
df_merged = pd.concat([preserved_old, new_only_records], ignore_index=True)

# Convert date columns
date_columns = ['PO Date', 'ETD']
for col in date_columns:
    if col in df_merged.columns:
        # Convert to datetime first, then extract date only for ETD
        df_merged[col] = pd.to_datetime(df_merged[col], errors='coerce')
        if col == 'ETD':
            df_merged[col] = df_merged[col].dt.date

# Print verification information
print("\nMerge Results:")
print(f"Final merged shape: {df_merged.shape}")
print(f"Records preserved from old file: {len(preserved_old)}")
print(f"New records added: {len(new_only_records)}")

# Save the result
df_merged.to_csv("updated_order_list.csv", index=False)

# Print sample of merged data
print("\nSample of preserved records (from old file):")
print(preserved_old[columns_to_keep].head())
print("\nSample of new records:")
print(new_only_records[columns_to_keep].head())