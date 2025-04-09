import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# -------------------------------
# Page Config and Styling
# -------------------------------
st.set_page_config(page_title="Order Guide", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .stSelectbox {max-width: 200px}
    .stTextInput {max-width: 300px}
    .main {padding: 0rem 1rem}
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Session State Initialization
# -------------------------------
if 'vendors' not in st.session_state:
    st.session_state.vendors = [
        {"id": 1, "name": "Gordon Food Service", "min_order": "$30 minimum"},
        {"id": 2, "name": "Sysco", "min_order": "$150 order minimum"},
        {"id": 3, "name": "US Foods", "min_order": "$50 minimum"}
    ]
if 'price_sheets' not in st.session_state:
    # Initialize with sample data
    sample_data = {
        1: pd.DataFrame({
            'Product name': ['Flank steak choice 193 raw ref'],
            'Vendor': ['Gordon Food Service'],
            'Delivery by': ['Wed, Mar 1'],
            'Unit price': ['$2.99/lb'],
            'Price': ['$88.99/cs'],
            'Category': ['Meat'],
            'Item Code': ['4385923'],
            'Delivery Time': ['8:00 AM - 12:00 PM']
        })
    }
    st.session_state.price_sheets = sample_data
if 'order_guide' not in st.session_state:
    st.session_state.order_guide = None

# -------------------------------
# Header Section
# -------------------------------
st.title("Order guide")
st.write("Manage your order guide, create shopping lists and place orders all in one place.")

col1, col2 = st.columns([2, 3])
with col1:
    location = st.selectbox("Location", ["San Francisco", "Oakland", "San Jose"])

# -------------------------------
# Navigation Tabs
# -------------------------------
tabs = st.tabs(["Your ingredients", "Vendor catalogs", "Price drops"])

with tabs[0]:  # Your ingredients tab
    # Search and Filter Section
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        search = st.text_input("Search", placeholder="Search products...")
    with col2:
        vendor_filter = st.selectbox("Vendor", ["All"] + [v["name"] for v in st.session_state.vendors])
    with col3:
        category_filter = st.selectbox("Categories", ["All", "Meat", "Vegetable", "Dairy", "Seafood"])
    with col4:
        st.write("")
        st.write("")
        export_btn = st.button("Export")

    # Product Categories
    def show_category(title, category_type):
        with st.expander(f"{title}", expanded=True):
            if st.session_state.order_guide is not None:
                df = st.session_state.order_guide[st.session_state.order_guide['Category'] == category_type]
                if not df.empty:
                    # Configure grid options
                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_default_column(
                        resizable=True,
                        filterable=True,
                        sorteable=True
                    )
                    gb.configure_selection(selection_mode='multiple', use_checkbox=True)
                    grid_options = gb.build()

                    # Display the grid
                    AgGrid(
                        df,
                        gridOptions=grid_options,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        height=150,
                        custom_css={
                            ".ag-header-cell-label": {"justify-content": "left"},
                            ".ag-cell": {"padding-left": "5px"}
                        }
                    )

    # Display product categories
    show_category("Steaks 🥩", "Meat")
    show_category("Prosciutto 🥓", "Meat")
    show_category("Yellow onions 🧅", "Vegetable")

with tabs[1]:  # Vendor catalogs tab
    st.write("Browse vendor catalogs and add items to your order guide.")
    
with tabs[2]:  # Price drops tab
    st.write("View current price drops and special offers.")