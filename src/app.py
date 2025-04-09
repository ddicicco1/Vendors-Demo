import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# -------------------------------
# Session State Initialization
# -------------------------------
if 'vendors' not in st.session_state:
    st.session_state.vendors = []  # Will hold vendor dictionaries: {"id": int, "name": str, "email": str}
if 'price_sheets' not in st.session_state:
    st.session_state.price_sheets = {}  # Maps vendor id to a pandas DataFrame
if 'order_guide' not in st.session_state:
    st.session_state.order_guide = None  # Will hold the combined order guide DataFrame

# -------------------------------
# Page Navigation Setup
# -------------------------------
st.set_page_config(page_title="Order Guide Prototype", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Add Vendor", "Upload Price Sheet", "Generate Order Guide", "View Order Guide"])

# -------------------------------
# Page 1: Add Vendor
# -------------------------------
def add_vendor():
    st.header("Add Vendor")
    st.write("Enter the vendor details below:")
    with st.form("vendor_form", clear_on_submit=True):
        vendor_name = st.text_input("Vendor Name")
        vendor_email = st.text_input("Vendor Email (optional)")
        submitted = st.form_submit_button("Add Vendor")
        if submitted:
            if vendor_name.strip() != "":
                # Generate a unique vendor ID using the next integer.
                vendor_id = len(st.session_state.vendors) + 1
                vendor = {"id": vendor_id, "name": vendor_name.strip(), "email": vendor_email.strip()}
                st.session_state.vendors.append(vendor)
                st.success(f"Vendor '{vendor_name}' added successfully!")
            else:
                st.error("Please provide a valid vendor name.")

    if st.session_state.vendors:
        st.subheader("Current Vendors")
        df_vendors = pd.DataFrame(st.session_state.vendors)
        st.table(df_vendors)

# -------------------------------
# Page 2: Upload Price Sheet per Vendor
# -------------------------------
def upload_price_sheet():
    st.header("Upload Price Sheet")
    if not st.session_state.vendors:
        st.info("No vendors available. Please add a vendor in the 'Add Vendor' section first.")
        return

    # Create a mapping for vendor selection.
    vendor_options = {vendor["name"]: vendor for vendor in st.session_state.vendors}
    selected_vendor_name = st.selectbox("Select a Vendor", list(vendor_options.keys()))
    selected_vendor = vendor_options[selected_vendor_name]

    uploaded_file = st.file_uploader("Upload a CSV Price Sheet", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.price_sheets[selected_vendor["id"]] = df
            st.success(f"Price sheet for vendor '{selected_vendor_name}' uploaded successfully.")
            st.write("Preview of uploaded file:")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

    # Display current uploads
    if st.session_state.price_sheets:
        st.subheader("Uploaded Price Sheets")
        # Create a quick summary list for vendors with uploads.
        uploaded_vendors = []
        for vendor in st.session_state.vendors:
            if vendor["id"] in st.session_state.price_sheets:
                uploaded_vendors.append({"Vendor": vendor["name"], "Rows": len(st.session_state.price_sheets[vendor["id"]])})
        if uploaded_vendors:
            st.table(pd.DataFrame(uploaded_vendors))

# -------------------------------
# Page 3: Generate Order Guide
# -------------------------------
def generate_order_guide():
    st.header("Generate Order Guide")
    if not st.session_state.price_sheets:
        st.info("No price sheets available. Please upload at least one price sheet in the 'Upload Price Sheet' section.")
        return

    all_dfs = []
    # Create a mapping from vendor id to vendor name
    vendor_map = {vendor["id"]: vendor["name"] for vendor in st.session_state.vendors}
    for vendor_id, df in st.session_state.price_sheets.items():
        # Make a copy and add a column for the vendor name
        temp_df = df.copy()
        temp_df["Vendor"] = vendor_map.get(vendor_id, "Unknown")
        all_dfs.append(temp_df)

    try:
        # For this example, we simply concatenate the data frames.
        # In a real scenario, you might merge or process these data frames further.
        order_guide_df = pd.concat(all_dfs, ignore_index=True)
        # Optionally sort the data (here we use the first column as an example).
        order_guide_df.sort_values(by=order_guide_df.columns[0], inplace=True)
        st.session_state.order_guide = order_guide_df
        st.success("Order guide generated successfully!")
        st.write("Preview of Order Guide:")
        st.dataframe(order_guide_df.head())
    except Exception as e:
        st.error(f"Error generating order guide: {e}")

# -------------------------------
# Page 4: View Order Guide
# -------------------------------
def view_order_guide():
    st.header("View Order Guide")
    if st.session_state.order_guide is None:
        st.info("No order guide generated yet. Please generate the order guide in the 'Generate Order Guide' section.")
        return

    df = st.session_state.order_guide.copy()

    # Global search input for filtering the order guide
    search_term = st.text_input("Global Search", value="")
    if search_term:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]

    # Build grid options for AgGrid (advanced interactive table)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True, sortable=True, resizable=True)
    grid_options = gb.build()

    AgGrid(
        df,
        gridOptions=grid_options,
        height=500,
        update_mode=GridUpdateMode.NO_UPDATE,
        theme='alpine'  # Options include 'alpine', 'light', 'dark', etc.
    )

# -------------------------------
# Main: Route to the Correct Page
# -------------------------------
if page == "Add Vendor":
    add_vendor()
elif page == "Upload Price Sheet":
    upload_price_sheet()
elif page == "Generate Order Guide":
    generate_order_guide()
elif page == "View Order Guide":
    view_order_guide()