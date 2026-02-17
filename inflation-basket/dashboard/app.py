
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.calculate_metrics import load_data, calculate_basket_metrics

st.set_page_config(page_title="Inflation Basket Dashboard", layout="wide")

st.title("🛒 Inflation Basket Dashboard")
st.markdown("Tracking daily prices of essential grocery items.")

# Load Data
df = load_data()

if df.empty:
    st.warning("No data available. Please run the scraper first.")
else:
    # Sidebar Filters
    st.sidebar.header("Filters")
    
    # Date Range Filter
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter data based on date
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
        df_filtered = df.loc[mask]
    else:
        df_filtered = df

    # Metrics
    metrics_df = calculate_basket_metrics(df_filtered)
    
    # Display Key Metrics
    col1, col2, col3 = st.columns(3)
    
    latest_date = df_filtered['date'].max()
    latest_metrics = metrics_df.loc[latest_date] if not metrics_df.empty and latest_date in metrics_df.index else None

    with col1:
        if latest_metrics is not None:
             st.metric("Latest Basket Cost", f"₹{latest_metrics['total_cost']:.2f}")
        else:
            st.metric("Latest Basket Cost", "N/A")
            
    with col2:
        if latest_metrics is not None:
            inflation = latest_metrics['inflation_rate']
            st.metric("Daily Inflation", f"{inflation:.2f}%" if pd.notna(inflation) else "0%")
        else:
            st.metric("Daily Inflation", "N/A")

    with col3:
        st.metric("Items Tracked", df_filtered['item_name'].nunique())

    # Tabs for Visualizations
    tab1, tab2, tab3 = st.tabs(["Price Trends", "Basket Cost Over Time", "Daily Inflation"])

    with tab1:
        st.subheader("Price Trend by Item")
        selected_items = st.multiselect("Select Items", df_filtered['item_name'].unique(), default=df_filtered['item_name'].unique())
        
        if selected_items:
            fig_price = px.line(df_filtered[df_filtered['item_name'].isin(selected_items)], 
                                x='date', y='price', color='item_name', markers=True,
                                title="Price History per Item")
            st.plotly_chart(fig_price, use_container_width=True)

    with tab2:
        st.subheader("Total Basket Cost Trend")
        if not metrics_df.empty:
            # Load Predictions
            predictions_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'predictions.csv')
            if os.path.exists(predictions_path):
                pred_df = pd.read_csv(predictions_path)
                pred_df['date'] = pd.to_datetime(pred_df['date'])
                
                # Check column name in predictions
                if 'predicted_cost' in pred_df.columns:
                     pred_df = pred_df.rename(columns={'predicted_cost': 'total_cost'})
                
                pred_df['type'] = 'Prediction'
                
                # Prepare historical data for chart
                hist_df = metrics_df.reset_index()[['date', 'total_cost']]
                hist_df['type'] = 'Historical'
                
                # Combine
                combined_df = pd.concat([hist_df, pred_df], ignore_index=True)
                
                fig_basket = px.line(combined_df, x='date', y='total_cost', color='type', markers=True,
                                     title="Total Basket Cost: Historical vs Predicted")
                
                # Add metric for 7-day forecast
                latest_pred = pred_df.iloc[-1]['total_cost']
                st.metric("Expected Basket Cost in 7 Days", f"₹{latest_pred:.2f}")
                
            else:
                fig_basket = px.line(metrics_df, x=metrics_df.index, y='total_cost', markers=True,
                                     title="Total Basket Cost Over Time")
            
            st.plotly_chart(fig_basket, use_container_width=True)

    with tab3:
        st.subheader("Daily Inflation Percentage")
        if not metrics_df.empty:
            fig_inflation = px.bar(metrics_df, x=metrics_df.index, y='inflation_rate',
                                   title="Daily Inflation Rate (%)")
            st.plotly_chart(fig_inflation, use_container_width=True)

    # Raw Data
    with st.expander("View Raw Data"):
        st.dataframe(df_filtered)
