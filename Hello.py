# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from babel.numbers import format_currency
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    #st.write("# Welcome to Streamlit! 👋")
    st.header('E-Commerce Public Dashboard :sparkles:')
    st.subheader('Daily Orders')

    
    data_df = pd.read_csv("main_data.csv")

    def created_monthly_orders_df(df):
        monthly_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
        })

        monthly_orders_df = monthly_orders_df.reset_index()
        monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
        }, inplace=True)

        return monthly_orders_df

    def create_order_perform_product_df(df):
        order_product_df = df.groupby("product_category_name").order_id.nunique().sort_values(ascending=True).reset_index()
        return order_product_df

    def create_order_perform_revenue_df(df):
        order_revenue_df = df.groupby("product_category_name").price.sum().sort_values(ascending=True).reset_index()
        return order_revenue_df

    def create_rmf_analysis_df(df):
        rmf_analysis = df.groupby(by="customer_id", as_index=False).agg({
            "order_purchase_timestamp": "max",
            "order_id": "nunique",
            "price": "sum"
        })
        rmf_analysis.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
        
        rmf_analysis["max_order_timestamp"] = rmf_analysis["max_order_timestamp"].dt.date
        recent_date = df["order_purchase_timestamp"].dt.date.max()
        rmf_analysis["recency"] = rmf_analysis["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
        rmf_analysis.drop("max_order_timestamp", axis=1, inplace=True)
        
        return rmf_analysis

    datetime_columns = ["order_purchase_timestamp"]
    data_df.sort_values(by="order_purchase_timestamp", inplace=True)
    data_df.reset_index(inplace=True)

    for column in datetime_columns:
        data_df[column] = pd.to_datetime(data_df[column])

    min_date = data_df["order_purchase_timestamp"].min()
    max_date = data_df["order_purchase_timestamp"].max()

    with st.sidebar:
        try:
            start_date, end_date = st.date_input(
                label='Time Span',min_value=min_date,
                max_value=max_date,
                value=[min_date, max_date]
        )
        except:
            start_date = min_date
            end_date = max_date

    main_df = data_df[(data_df["order_purchase_timestamp"] >= str(start_date)) & 
                    (data_df["order_purchase_timestamp"] <= str(end_date))]
    
    order_perform_product_df = create_order_perform_product_df(main_df)
    order_perform_revenue_df = create_order_perform_revenue_df(main_df)
    monthly_orders_df = created_monthly_orders_df(main_df)
    rmf_analysis_df = create_rmf_analysis_df(main_df)

    col1, col2 = st.columns(2)

    with col1:
        total_orders = monthly_orders_df.order_count.sum()
        st.metric("Total orders", value=total_orders)

    with col2:
        total_revenue = format_currency(monthly_orders_df.revenue.sum(), "$", locale='en_US')
        st.metric("Total Revenue", value=total_revenue)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        monthly_orders_df["order_purchase_timestamp"],
        monthly_orders_df["order_count"],
        marker='o', 
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

if __name__ == "__main__":
    run()
