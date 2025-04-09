import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# -------------------------------
# Page Config and Styling
# -------------------------------
st.set_page_config(page_title="Order Guide Wizard", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .step-header {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        color: #0066cc;
    }
    .step-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .complete-step {
        color: #28a745;
        font-size: 0.9rem;
    }
    .stProgress .st-bo {
        background-color: #0066cc;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Session State Initialization
# -------------------------------
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'vendors' not in st.session_state:
    st.session_state.vendors = []
if 'price_sheets' not in st.session_state:
    st.session_state.price_sheets = {}
if 'order_guide' not in st.session_state:
    st.session_state.order_guide = None

# -------------------------------
# Progress Bar and Navigation
# -------------------------------
st.title("Order Guide Setup Wizard")
progress_value = (st.session_state.current_step - 1) * 25
st.progress(progress_value / 100)

# Step indicators
cols = st.columns(4)
for i, step in enumerate(["Add Vendor", "Upload Price Sheet", "Generate Guide", "View Guide"], 1):
    with cols[i-1]:
        if i < st.session_state.current_step:
            st.markdown(f"✅ Step {i}: {step}")
        elif i == st.session_state.current_step:
            st.markdown(f"**👉 Step {i}: {step}**")
        else:
            st.markdown(f"Step {i}: {step}")

st.markdown("---")

# -------------------------------
# Step 1: Add Vendor
# -------------------------------
def render_step_1():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<p class="step-header">Step 1: Add Vendor Details</p>', unsafe_allow_html=True)
    
    with st.form("vendor_form", clear_on_submit=True):
        vendor_name = st.text_input("Vendor Name")
        min_order = st.text_input("Minimum Order (e.g., $50 minimum)")
        submitted = st.form_submit_button("Add Vendor")
        
        if submitted and vendor_name.strip():
            vendor_id = len(st.session_state.vendors) + 1
            vendor = {
                "id": vendor_id,
                "name": vendor_name.strip(),
                "min_order": min_order.strip()
            }
            st.session_state.vendors.append(vendor)
            st.success(f"Vendor '{vendor_name}' added successfully!")

    if st.session_state.vendors:
        st.subheader("Current Vendors")
        df_vendors = pd.DataFrame(st.session_state.vendors)
        st.table(df_vendors)
        
        if st.button("Next: Upload Price Sheets →"):
            st.session_state.current_step = 2
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# Step 2: Upload Price Sheet
# -------------------------------
def render_step_2():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<p class="step-header">Step 2: Upload Price Sheets</p>', unsafe_allow_html=True)
    
    if not st.session_state.vendors:
        st.warning("Please add at least one vendor first.")
        if st.button("← Back to Add Vendor"):
            st.session_state.current_step = 1
            st.rerun()
        return

    vendor_options = {vendor["name"]: vendor for vendor in st.session_state.vendors}
    selected_vendor_name = st.selectbox("Select Vendor", list(vendor_options.keys()))
    selected_vendor = vendor_options[selected_vendor_name]

    uploaded_file = st.file_uploader("Upload Price Sheet (CSV)", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            # Add vendor information to the dataframe
            df['Vendor'] = selected_vendor["name"]
            df['Min Order'] = selected_vendor["min_order"]
            st.session_state.price_sheets[selected_vendor["id"]] = df
            st.success(f"Price sheet for {selected_vendor_name} uploaded successfully!")
            st.write("Preview:")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    if st.session_state.price_sheets:
        st.subheader("Uploaded Price Sheets")
        for vendor in st.session_state.vendors:
            if vendor["id"] in st.session_state.price_sheets:
                st.write(f"✅ {vendor['name']}: {len(st.session_state.price_sheets[vendor['id']])} items")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Add Vendor"):
            st.session_state.current_step = 1
            st.rerun()
    with col2:
        if st.session_state.price_sheets and st.button("Next: Generate Order Guide →"):
            st.session_state.current_step = 3
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# Step 3: Generate Order Guide
# -------------------------------
def render_step_3():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<p class="step-header">Step 3: Generate Order Guide</p>', unsafe_allow_html=True)
    
    if not st.session_state.price_sheets:
        st.warning("Please upload at least one price sheet first.")
        if st.button("← Back to Upload Price Sheets"):
            st.session_state.current_step = 2
            st.rerun()
        return

    if st.button("Generate Order Guide"):
        try:
            all_dfs = []
            for vendor_id, df in st.session_state.price_sheets.items():
                vendor = next((v for v in st.session_state.vendors if v["id"] == vendor_id), None)
                if vendor:
                    df_copy = df.copy()
                    df_copy["Vendor"] = vendor["name"]
                    df_copy["Min Order"] = vendor["min_order"]
                    all_dfs.append(df_copy)

            if all_dfs:
                st.session_state.order_guide = pd.concat(all_dfs, ignore_index=True)
                st.success("Order guide generated successfully!")
                st.write("Preview:")
                st.dataframe(st.session_state.order_guide.head())
                
                if st.button("Next: View Order Guide →"):
                    st.session_state.current_step = 4
                    st.rerun()
        except Exception as e:
            st.error(f"Error generating order guide: {e}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Upload Price Sheets"):
            st.session_state.current_step = 2
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# Step 4: View Order Guide
# -------------------------------
def render_step_4():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<p class="step-header">Step 4: View and Filter Order Guide</p>', unsafe_allow_html=True)
    
    if st.session_state.order_guide is None:
        st.warning("Please generate the order guide first.")
        if st.button("← Back to Generate Order Guide"):
            st.session_state.current_step = 3
            st.rerun()
        return

    # Search and Filter Section
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        search = st.text_input("Search products...")
    with col2:
        vendor_filter = st.selectbox("Vendor", ["All"] + [v["name"] for v in st.session_state.vendors])
    with col3:
        categories = ["All"] + list(st.session_state.order_guide["Category"].unique()) if "Category" in st.session_state.order_guide.columns else ["All"]
        category_filter = st.selectbox("Categories", categories)
    with col4:
        st.write("")
        st.write("")
        export_btn = st.button("Export")

    # Apply filters
    df = st.session_state.order_guide.copy()
    if search:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    if vendor_filter != "All":
        df = df[df["Vendor"] == vendor_filter]
    if category_filter != "All" and "Category" in df.columns:
        df = df[df["Category"] == category_filter]

    # Display the order guide using AgGrid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sorteable=True,
        width=150
    )
    gb.configure_selection(selection_mode='multiple', use_checkbox=True)
    grid_options = gb.build()

    AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=400
    )

    if st.button("← Back to Generate Order Guide"):
        st.session_state.current_step = 3
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# Render Current Step
# -------------------------------
if st.session_state.current_step == 1:
    render_step_1()
elif st.session_state.current_step == 2:
    render_step_2()
elif st.session_state.current_step == 3:
    render_step_3()
else:
    render_step_4()