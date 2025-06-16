import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Malaika Purchase Order Manager")

# Custom CSS for highlighting
st.markdown("""
    <style>
    .customer-order { background-color: rgba(255, 0, 0, 0.2) !important; }
    .past-etd { background-color: rgba(0, 255, 0, 0.2) !important; }
    </style>
""", unsafe_allow_html=True)

# Load data
try:
    df = pd.read_csv("updated_order_list.csv")
    
    # Convert date columns with proper error handling
    date_columns = ['PO Date', 'ETD']
    for col in date_columns:
        if col in df.columns:
            # Convert to datetime and extract date only for display
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
            
    # Ensure all required columns exist
    required_columns = [
        "Purchase Order", "Product", "Variant", "SKU", "PO Date", 
        "Quantity", "ETD", "Comment", "Customer Order"
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
            
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Tabs for editing and viewing
tab1, tab2 = st.tabs(["Edit View", "Full Table View"])

with tab1:
    st.write("Edit ETD, Comments, Quantity and Customer Order status below:")
    
    # Keep track of rows to delete
    rows_to_delete = []

    for idx in df.index:
        with st.expander(f"Order ID: {df.at[idx, 'Purchase Order']} — {df.at[idx, 'Product']} ({df.at[idx, 'SKU']})"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                etd = st.date_input(
                    f"ETD",
                    df.at[idx, "ETD"] if pd.notna(df.at[idx, "ETD"]) else None,
                    key=f"etd_{idx}"
                )
            
            with col2:
                comment = st.text_input(
                    "Comment",
                    value=df.at[idx, "Comment"] if pd.notna(df.at[idx, "Comment"]) else "",
                    key=f"comment_{idx}"
                )
            
            with col3:
                quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    value=int(df.at[idx, "Quantity"]) if pd.notna(df.at[idx, "Quantity"]) else 0,
                    key=f"quantity_{idx}"
                )
            
            with col4:
                customer_order = st.selectbox(
                    "Customer Order",
                    options=["", "Yes", "No"],
                    index=0 if df.at[idx, "Customer Order"] == "" else 
                          1 if df.at[idx, "Customer Order"] == "Yes" else 2,
                    key=f"customer_order_{idx}"
                )
            
            # Add delete button for each row
            if st.button("🗑️ Delete Row", key=f"delete_{idx}"):
                rows_to_delete.append(idx)
            
            # Update dataframe
            df.at[idx, "ETD"] = etd
            df.at[idx, "Comment"] = comment
            df.at[idx, "Quantity"] = quantity
            df.at[idx, "Customer Order"] = customer_order

    # Remove marked rows
    if rows_to_delete:
        df = df.drop(rows_to_delete)
        st.warning(f"Deleted {len(rows_to_delete)} row(s)")
        rows_to_delete = []  # Reset the list

    # Save changes
    if st.button("Save Changes"):
        try:
            df.to_csv("updated_order_list.csv", index=False)
            st.success("Changes saved successfully!")
        except Exception as e:
            st.error(f"Error saving changes: {str(e)}")

with tab2:
    st.write("Full table preview")

    # Apply conditional formatting
    def highlight_rows(row):
        if row["Customer Order"] == "Yes":
            return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
        elif pd.notna(row["ETD"]) and row["ETD"] <= datetime.now().date():
            return ['background-color: rgba(0, 255, 0, 0.2)'] * len(row)
        return [''] * len(row)

    # Create styled dataframe with selected columns for display
    display_columns = [
        "Purchase Order", "Product", "Variant", "SKU", "PO Date",
        "Quantity", "ETD", "Comment", "Customer Order"
    ]
    
    styled_df = df[display_columns].style.apply(highlight_rows, axis=1)
    st.dataframe(styled_df, use_container_width=True)