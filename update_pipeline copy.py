import pandas as pd
from openpyxl import load_workbook

# Load old and new data
df_old = pd.read_excel("Open_purchase_order_items_June_3rd(1).xlsx", engine='openpyxl')

df_new = pd.read_csv("purchase_items(6).csv")

# Ensure Ready and Comment columns exist in df_old
"""for col in ["Ready", "Comment"]:
    if col not in df_old.columns:
        df_old[col] = """""

df_new = df_new.drop(columns=["Ready", "Comment"], errors="ignore")

# Define keys to match rows
merge_keys = ["Purchase Order", "SKU"]

# Keep only rows from old that are still in new by Purchase Order
df_old_filtered = df_old[df_old["Purchase Order"].isin(df_new["Purchase Order"])]

# Determine which optional columns are available
optional_cols = [col for col in ["Ready", "Comment", "Status"] if col in df_old_filtered.columns]
df_merged = pd.merge(
    df_new,
    df_old_filtered[merge_keys + optional_cols],
    on=merge_keys,
    how="left"
)

# Fill missing fields with empty strings
df_merged["Ready"] = df_merged["Ready"].fillna("")
df_merged["Comment"] = df_merged["Comment"].fillna("")

if "Status" in df_merged.columns:
    df_merged.rename(columns={"Status": "Status Note"}, inplace=True)
if "Status Note" not in df_merged.columns:
    df_merged["Status Note"] = ""

# Keep only columns from df_new + the appended ones
final_columns = [col if col != "Status" else "Status Note" for col in df_new.columns] + ["Ready", "Comment", "Status Note"]
df_merged = df_merged[final_columns]

# Save updated file
df_merged.to_csv("updated_order_list.csv", index=False)