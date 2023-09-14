from typing import List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st


def set_page_config():
    st.set_page_config(
        page_title="Sales Dashboard",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    """, unsafe_allow_html=True)


@st.cache_data
def load_data() -> pd.DataFrame:
    file_name = 'https://raw.githubusercontent.com/diogo-costa-silva/datasets/main/sales_data_sample.csv'
    data = pd.read_csv(file_name, encoding='latin1')
    data['ORDERDATE'] = pd.to_datetime(data['ORDERDATE'])
    return data


def filter_data(data: pd.DataFrame, column: str, values: List[str]) -> pd.DataFrame:
    return data[data[column].isin(values)] if values else data


@st.cache_data
def calculate_kpis(data: pd.DataFrame) -> List[float]:
    total_sales = data['SALES'].sum()
    sales_in_m = f"{total_sales / 1000000:.2f}M"
    total_orders = data['ORDERNUMBER'].nunique()
    average_sales_per_order = f"{total_sales / total_orders / 1000:.2f}K"
    unique_customers = data['CUSTOMERNAME'].nunique()
    return [sales_in_m, total_orders, average_sales_per_order, unique_customers]


def display_kpi_metrics(kpis: List[float], kpi_names: List[str]):
    st.header("KPI Metrics")
    for i, (col, (kpi_name, kpi_value)) in enumerate(zip(st.columns(4), zip(kpi_names, kpis))):
        col.metric(label=kpi_name, value=kpi_value)




def display_sidebar(data: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    st.sidebar.markdown(
    """
    <a href="https://www.linkedin.com/in/diogo-costa-e-silva/" target="_blank" style="text-decoration: none;">
        <div style="display: flex; align-items: center;">
            <i class="fab fa-linkedin" style="font-size: 22px; margin-right: 5px; color: #FF4C4B;"></i>
            <span style="font-size: 20px; margin-left: 5px; color: #FF4C4B">Check me out on LinkedIn!</span>
        </div>
    </a>
    """, unsafe_allow_html=True
    )
    st.sidebar.header("Filters")

    if 'end_date' not in locals():
        end_date = pd.Timestamp(data['ORDERDATE'].max().date())

    start_date = pd.Timestamp(st.sidebar.date_input("Start date", value=data['ORDERDATE'].min().date(), max_value=end_date.date()))
    end_date = pd.Timestamp(st.sidebar.date_input("End date", value=end_date.date(), min_value=start_date.date(), max_value=data['ORDERDATE'].max().date()))
    
    product_lines = sorted(data['PRODUCTLINE'].unique())
    selected_product_lines = st.sidebar.multiselect("Product lines", product_lines, product_lines)

    selected_countries = st.sidebar.multiselect("Select Countries", data['COUNTRY'].unique())

    selected_statuses = st.sidebar.multiselect("Select Order Statuses", data['STATUS'].unique())

    # Introduce whitespace to push the markdown to the bottom
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # Create by Diogo Silva
    st.sidebar.markdown(
        """
        <style>
        .info-text {
            background-color: #FF4C4B;
            color: #1F2232;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
        <p class="info-text">Created by Diogo Silva</p>
        """,
        unsafe_allow_html=True
    )


    # st.sidebar.info('<span style="color: red;">Created by Diogo Silva</span>', unsafe_allow_html=True)

    return selected_product_lines, selected_countries, selected_statuses, start_date, end_date



def display_charts(data: pd.DataFrame):
    combine_product_lines = st.checkbox("Combine Product Lines", value=True)

    if combine_product_lines:
        fig = px.area(data, x='ORDERDATE', y='SALES',
                      title="Sales by Product Line Over Time", width=900, height=500)
    else:
        fig = px.area(data, x='ORDERDATE', y='SALES', color='PRODUCTLINE',
                      title="Sales by Product Line Over Time", width=900, height=500)

    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    fig.update_xaxes(rangemode='tozero', showgrid=False)
    fig.update_yaxes(rangemode='tozero', showgrid=True)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Top 10 Customers")
        top_customers = data.groupby('CUSTOMERNAME')['SALES'].sum().reset_index().sort_values('SALES',
                                                                                              ascending=False).head(10)
        st.write(top_customers)

    with col2:
        st.subheader("Top 10 Products by Sales")
        top_products = data.groupby(['PRODUCTCODE', 'PRODUCTLINE'])['SALES'].sum().reset_index().sort_values('SALES',
                                                                                                             ascending=False).head(
            10)
        st.write(top_products)

    with col3:
        st.subheader("Total Sales by Product Line")
        total_sales_by_product_line = data.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
        st.write(total_sales_by_product_line)



def main():
    set_page_config()

    data = load_data()

    st.title("📊 Sales Dashboard")

    selected_product_lines, selected_countries, selected_statuses, start_date, end_date = display_sidebar(data)

    filtered_data = data.copy()
    
    # Filtering by date range
    filtered_data = filtered_data[(filtered_data['ORDERDATE'] >= start_date) & (filtered_data['ORDERDATE'] <= end_date)]
    
    filtered_data = filter_data(filtered_data, 'PRODUCTLINE', selected_product_lines)
    filtered_data = filter_data(filtered_data, 'COUNTRY', selected_countries)
    filtered_data = filter_data(filtered_data, 'STATUS', selected_statuses)

    kpis = calculate_kpis(filtered_data)
    kpi_names = ["Total Sales", "Total Orders", "Average Sales per Order", "Unique Customers"]
    display_kpi_metrics(kpis, kpi_names)

    display_charts(filtered_data)

if __name__ == '__main__':
    main()