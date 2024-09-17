import streamlit as st
import pandas as pd
import plotly.express as px

# Set up the title and description
st.title('Interactive Sales Forecasting and Reporting Dashboard')
st.write('Upload your sales data to analyze trends and forecast stock with interactive charts.')

# Allow the user to upload a CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV
    sales_data = pd.read_csv(uploaded_file)

    # Convert 'day' to a datetime type and extract month for grouping
    sales_data['day'] = pd.to_datetime(sales_data['day'])
    sales_data['month'] = sales_data['day'].dt.to_period('M').astype(str)  # Convert to string

    # Show monthly sales metrics
    st.subheader('Monthly Sales Metrics')
    monthly_sales = sales_data.groupby('month')['total_sales'].sum().reset_index()
    fig_monthly_sales = px.bar(
        monthly_sales, 
        x='month', 
        y='total_sales', 
        title='Monthly Sales', 
        labels={'month': 'Month', 'total_sales': 'Total Sales ($)'}, 
        template="plotly_white"
    )
    st.plotly_chart(fig_monthly_sales)

    # Sales Data Overview
    st.subheader('Sales Data Overview')
    num_top_products = st.slider("Select how many top products to display", 5, 20, 10)
    top_products_by = st.selectbox("View top products by", ["Total Sales", "Quantity Sold"])
    
    if top_products_by == "Total Sales":
        top_products = sales_data.groupby('product_title')['total_sales'].sum().nlargest(num_top_products).reset_index()
    else:
        top_products = sales_data.groupby('product_title')['net_quantity'].sum().nlargest(num_top_products).reset_index()
    
    st.write(f"Top {num_top_products} products by {top_products_by}:")
    
    # Plot interactive bar chart using Plotly
    fig_top_products = px.bar(
        top_products,
        x='product_title',
        y='total_sales' if top_products_by == "Total Sales" else 'net_quantity',
        title=f"Top {num_top_products} Products by {top_products_by}",
        labels={'product_title': 'Product', 'total_sales': 'Total Sales ($)', 'net_quantity': 'Quantity Sold'},
        template="plotly_white"
    )
    st.plotly_chart(fig_top_products)

    # Filter options by product type and vendor with "Any" option
    st.subheader('Filter by Product Type and Vendor')
    product_types = ["Any"] + list(sales_data['product_type'].unique())
    vendors = ["Any"] + list(sales_data['product_vendor'].unique())

    selected_product_type = st.selectbox("Select Product Type", options=product_types)
    selected_vendor = st.selectbox("Select Vendor", options=vendors)

    # Filter data based on the selections
    filtered_data = sales_data.copy()
    if selected_product_type != "Any":
        filtered_data = filtered_data[filtered_data['product_type'] == selected_product_type]
    if selected_vendor != "Any":
        filtered_data = filtered_data[filtered_data['product_vendor'] == selected_vendor]

    st.write(f"Showing data for product type: **{selected_product_type}** and vendor: **{selected_vendor}**")
    st.write(filtered_data)

    # Plot: Sales by Product Title
    st.subheader('Total Sales by Product Title')
    product_sales = filtered_data.groupby('product_title')['total_sales'].sum().sort_values(ascending=False).reset_index()

    # Check if there's any data to plot
    if not product_sales.empty:
        fig_product_sales = px.bar(
            product_sales,
            x='product_title',
            y='total_sales',
            title='Total Sales by Product Title',
            labels={'product_title': 'Product', 'total_sales': 'Total Sales ($)'},
            template="plotly_white"
        )
        st.plotly_chart(fig_product_sales)
    else:
        st.write("No sales data available for the selected filters.")

    # Sales Trends Over Time for a Selected Product
    st.subheader('View Sales Trends Over Time')
    selected_product = st.selectbox("Select a product to view its sales trend", options=sales_data['product_title'].unique())
    
    # Filter data by selected product and group by day
    product_trend_data = sales_data[sales_data['product_title'] == selected_product].groupby('day')['net_quantity'].sum().reset_index()

    # Check if there's any data to plot
    if not product_trend_data.empty:
        fig_sales_trend = px.line(
            product_trend_data,
            x='day',
            y='net_quantity',
            title=f'Sales Trend Over Time for {selected_product}',
            labels={'day': 'Day', 'net_quantity': 'Quantity Sold'},
            template="plotly_white"
        )
        st.plotly_chart(fig_sales_trend)
    else:
        st.write(f"No sales data available for {selected_product} over time.")

    # Stocking Requirements: Master Planning Schedule (MPS)
    st.subheader('Stocking Requirements (Master Planning Schedule)')
    st.write("This section suggests stocking requirements based on sales velocity and expected demand.")

    # Calculate average daily sales (sales velocity) for each product
    sales_velocity = sales_data.groupby('product_title')['net_quantity'].sum() / 90  # Assuming 90 days in the dataset
    mps_data = pd.DataFrame(sales_velocity, columns=['Sales Velocity (units/day)']).reset_index()

    # Allow the user to input stocking plans
    mps_data['Stocking Plan (units)'] = st.number_input('Enter Stocking Plan for Products', value=100, step=10, format="%d")
    
    # Monthly demand prediction
    mps_data['Predicted Monthly Demand'] = mps_data['Sales Velocity (units/day)'] * 30  # Predicted for the next month

    # Highlight critical items: overstocked (green), understocked (red)
    mps_data['Status'] = mps_data.apply(
        lambda row: 'Understocked' if row['Predicted Monthly Demand'] > row['Stocking Plan (units)'] else 'Well-stocked', axis=1
    )
    
    # Color the rows based on the status
    def highlight_critical(s):
        if s == 'Understocked':
            return 'background-color: red'
        elif s == 'Well-stocked':
            return 'background-color: green'
        return ''

    st.write(mps_data.style.applymap(highlight_critical, subset=['Status']))

else:
    st.write("Please upload a sales data file to proceed.")
