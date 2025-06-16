import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# Password protection logic
correct_password = "sunlight42"
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔒 Access Protected")
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == correct_password:
            st.session_state["auth"] = True
            st.experimental_rerun()
        else:
            st.error("Incorrect password")
    st.stop()  # Stop execution if not authenticated

# Main application (only runs if authenticated)
st.title("Malaika Purchase Order Manager")

# Custom CSS for highlighting
st.markdown("""
    <style>
    .customer-order { background-color: rgba(255, 0, 0, 0.2) !important; }
    .past-etd { background-color: rgba(0, 255, 0, 0.2) !important; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv("updated_order_list.csv")
        date_columns = ['PO Date', 'ETD']
        for col in date_columns:
            if col in st.session_state.df.columns:
                st.session_state.df[col] = pd.to_datetime(st.session_state.df[col], errors='coerce').dt.date
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

if 'rows_to_delete' not in st.session_state:
    st.session_state.rows_to_delete = set()

def delete_row(idx):
    st.session_state.df = st.session_state.df.drop(index=idx)
    st.session_state.rows_to_delete.add(idx)

# Tabs for editing and viewing
tab1, tab2 = st.tabs(["Edit View", "Full Table View"])

with tab1:
    st.write("Edit ETD, Comments, Quantity and Customer Order status below:")
    
    # Display only non-deleted rows
    for idx in st.session_state.df.index:
        with st.expander(f"Order ID: {st.session_state.df.at[idx, 'Purchase Order']} — {st.session_state.df.at[idx, 'Product']} ({st.session_state.df.at[idx, 'SKU']})"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                etd = st.date_input(
                    f"ETD",
                    st.session_state.df.at[idx, "ETD"] if pd.notna(st.session_state.df.at[idx, "ETD"]) else None,
                    key=f"etd_{idx}"
                )
            
            with col2:
                comment = st.text_input(
                    "Comment",
                    value=st.session_state.df.at[idx, "Comment"] if pd.notna(st.session_state.df.at[idx, "Comment"]) else "",
                    key=f"comment_{idx}"
                )
            
            with col3:
                quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    value=int(st.session_state.df.at[idx, "Quantity"]) if pd.notna(st.session_state.df.at[idx, "Quantity"]) else 0,
                    key=f"quantity_{idx}"
                )
            
            with col4:
                customer_order = st.selectbox(
                    "Customer Order",
                    options=["", "Yes", "No"],
                    index=0 if st.session_state.df.at[idx, "Customer Order"] == "" else 
                          1 if st.session_state.df.at[idx, "Customer Order"] == "Yes" else 2,
                    key=f"customer_order_{idx}"
                )
            
            if st.button("🗑️ Delete Row", key=f"delete_{idx}"):
                delete_row(idx)
                st.experimental_rerun()
            
            # Update dataframe
            st.session_state.df.at[idx, "ETD"] = etd
            st.session_state.df.at[idx, "Comment"] = comment
            st.session_state.df.at[idx, "Quantity"] = quantity
            st.session_state.df.at[idx, "Customer Order"] = customer_order

    # Save changes
    if st.button("Save Changes"):
        try:
            st.session_state.df.to_csv("updated_order_list.csv", index=False)
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