import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set up the title and description
st.title('Sales Forecasting and Reporting Dashboard')
st.write('Upload your sales data to analyze trends and forecast stock.')

# Allow the user to upload a CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV
    sales_data = pd.read_csv(uploaded_file)

    # Display some basic statistics about the sales data
    st.subheader('Sales Data Overview')
    st.write(sales_data.head())

    # Show overall metrics
    st.subheader('Overall Sales Metrics')
    total_sales = sales_data['total_sales'].sum()
    total_quantity = sales_data['net_quantity'].sum()
    top_product = sales_data.loc[sales_data['net_quantity'].idxmax(), 'product_title']

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Sales", value=f"${total_sales:,.2f}")
    col2.metric(label="Total Quantity Sold", value=f"{total_quantity}")
    col3.metric(label="Top Selling Product", value=top_product)

    # Filter options by product type and vendor
    st.subheader('Filter by Product Type and Vendor')
    product_types = sales_data['product_type'].unique()
    vendors = sales_data['product_vendor'].unique()

    selected_product_type = st.selectbox("Select Product Type", options=product_types)
    selected_vendor = st.selectbox("Select Vendor", options=vendors)

    filtered_data = sales_data[
        (sales_data['product_type'] == selected_product_type) & 
        (sales_data['product_vendor'] == selected_vendor)
    ]

    st.write(f"Showing data for product type: **{selected_product_type}** and vendor: **{selected_vendor}**")
    st.write(filtered_data)

    # Plot: Sales by Product Title
st.subheader('Total Sales by Product Title')
product_sales = filtered_data.groupby('product_title')['total_sales'].sum().sort_values(ascending=False)

# Check if there's any data to plot
if not product_sales.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    product_sales.plot(kind='bar', ax=ax)
    ax.set_title('Total Sales by Product Title')
    ax.set_ylabel('Sales ($)')
    ax.set_xlabel('Product Title')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)
else:
    st.write("No sales data available for the selected filters.")

else:
    st.write("Please upload a sales data file to proceed.")
