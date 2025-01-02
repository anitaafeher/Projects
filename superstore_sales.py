import streamlit as st
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from matplotlib.ticker import ScalarFormatter
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import json
import plotly.figure_factory as ff

def get_data():
    data = pd.read_csv(r'C:\CodeCool\data analisys techniques\superstore-python-anitaafeher\data.csv', delimiter=',')
    return data

def processing_data(df):
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True) 
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True) 
    df['Ship Date'] = df.apply(
        lambda row: row['Order Date'] if row['Ship Date'] < row['Order Date'] else row['Ship Date'], axis=1)
    df['Ship Date'] = df.apply(
        lambda row: row['Order Date'] + pd.Timedelta(days=1) if row['Ship Date'] <= row['Order Date'] else row['Ship Date'], axis=1)
    df['Year'] = df['Order Date'].dt.year
    df['Days to Ship'] = (df['Ship Date'] - df['Order Date']).dt.days
    return df

def calculate_metrics(df):
    total_sales = df['Sales'].sum()
    total_sales_millified = "${:,.1f}M".format(total_sales/1_000_000)
    total_profit = df['Profit'].sum()
    total_profit_millified = "${:,.1f}k".format(total_profit/1_000)
    number_of_orders = df['Order ID'].nunique()
    return total_sales_millified, total_profit_millified, number_of_orders

def top_ten(df):
    top_ten_sales = df.groupby('Product Name')[['Sales']].sum()
    top_ten_product_sales = top_ten_sales.sort_values('Sales', ascending=False).head(10)
    top_ten_profit = df.groupby('Product Name')[['Profit']].sum()
    top_ten_product_profit = top_ten_profit.sort_values('Profit', ascending=False).head(10)
    return top_ten_product_sales, top_ten_product_profit

def year_filter(df):
    if year == "All":
        return df
    return df[df['Year'] == year]


def zip_to_fip(df):
    zip_to_fips_path = 'C:\CodeCool\data analisys techniques\superstore-python-anitaafeher\zip2fips.json'
    with open(zip_to_fips_path, 'r') as file:
        zip_to_fips = json.load(file)
    zip_to_fips_df = pd.DataFrame(list(zip_to_fips.items()), columns=['Postal Code', 'FIPS'])
    df['Postal Code'] = df['Postal Code'].fillna(0).astype(int).astype(str).str.zfill(5)
    zip_to_fips_df['Postal Code'] = zip_to_fips_df['Postal Code'].astype(str).str.zfill(5)
    df = df.merge(zip_to_fips_df, on='Postal Code', how='left')
    choropleth_data = df.groupby('FIPS', as_index=False)['Sales'].sum()
    return choropleth_data

def set_menu():
    st.session_state['menu'] = st.session_state['menu_selected']

def set_year():
    st.session_state['year'] = st.session_state['year_selected']

COLOR_SCALE = "twilight"

if 'menu' not in st.session_state:
    st.session_state['menu'] = 'Overview'
if 'year' not in st.session_state:
    st.session_state['year'] = "All"

df = get_data()
df = processing_data(df)

menu = st.sidebar.radio(
    "Navigation",
    options=["Overview", "Top products", "Country statistics", "Trends"],
    index=["Overview", "Top products", "Country statistics", "Trends"].index(st.session_state['menu']),
    key='menu_selected',
    on_change=set_menu
)

years = ["All"] + list(df['Year'].unique())
year = st.sidebar.selectbox(
    'Year',
    options=years,
    index=years.index(st.session_state['year']),
    key='year_selected',
    on_change=set_year
)

df = year_filter(df)

sales, profit, orders = calculate_metrics(df)
top_ten_sales, top_ten_profit = top_ten(df)

#Horizontal barchart for top 10 products by sales

#fig, ax = plt.subplots(figsize=(8,8))
#ax.barh(top_ten_sales.index, top_ten_sales['Sales'], color='blue', edgecolor='darkblue')
#ax.set_title('Top 10 Products by Sales')
#ax.set_xlabel('Sales')
#ax.set_ylabel('Product')
#ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
#plt.gca().invert_yaxis()

top_ten_sales = top_ten_sales.sort_values('Sales', ascending=True)
fig1 = px.bar(
    top_ten_sales,
    x='Sales',
    orientation='h',
    title='Top 10 Products by Sales',
    color=top_ten_sales['Sales'],
    color_continuous_scale=COLOR_SCALE
)

fig1.update_traces(
    hovertemplate='%{x}<extra></extra>'
)

#Horizontal bar chart for top 10 products by profit

#fig1, ax1 = plt.subplots(figsize=(8,8))
#ax1.barh(top_ten_profit.index, top_ten_profit['Profit'], color='blue', edgecolor='darkblue')
#ax1.set_title('Top 10 Products by Profit')
#ax1.set_xlabel('Profit')
#ax1.set_ylabel('Product')
#ax1.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
#plt.gca().invert_yaxis()

top_ten_profit = top_ten_profit.sort_values('Profit', ascending=True)
fig2 = px.bar(
    top_ten_profit,
    x='Profit',
    orientation='h',
    title='Top 10 Products by Profit',
    color=top_ten_profit['Profit'],
    color_continuous_scale=COLOR_SCALE
)
fig2.update_traces(
    hovertemplate='%{x}<extra></extra>'
)

#Average shipping days

average_shipping = df['Days to Ship'].mean()
min_days = df['Days to Ship'].min()
max_days = df['Days to Ship'].max()
fig3 = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = average_shipping,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Days to Ship"},
    gauge = {'axis': {'range': [min_days, max_days], 'tickcolor': "darkblue"},
            'bar': {'color': "green"},
            'steps': [
                {'range': [min_days, max_days], 'color': "gray"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_days}}))   


# pie chartok a szegmensekről

segment_df = df.groupby('Segment', as_index=False)['Order ID'].count()
fig8 = px.pie(
    segment_df,
    names='Segment',         
    values='Order ID',
    title='Orders by segments',       
    color_discrete_sequence=px.colors.sequential.RdBu)

segment_df = df.groupby('Segment', as_index=False)['Profit'].sum()
fig9 = px.pie(
    segment_df,
    names='Segment',         
    values='Profit',
    title='Profit by segments',         
    color_discrete_sequence=px.colors.sequential.RdBu)


# sales trend

sales_trend = df.groupby(['Category', 'Year'])['Sales'].sum().reset_index()
#sales_pivot = pd.pivot_table(sales_trend, values='Sales', index='Year', columns='Category')
#fig4, ax4 = plt.subplots(figsize=(8,8))
#sales_pivot.plot.bar(stacked= True, color=['blue', 'green', 'orange'], ax=ax4)
#ax4.set_title('Sales Trends')
#ax4.set_xlabel('Years')
#ax4.set_ylabel('Sales')
#ax4.legend(title='Category')
#plt.xticks(rotation=0)

fig4 = px.bar(
    sales_trend,
    x='Year',
    y='Sales',
    color='Category',
    title='Sales Trends',
    labels={'Sales': 'Sales', 'Year': 'Years'},
    barmode='stack',
    color_continuous_scale=COLOR_SCALE)

fig4.update_traces(
    hovertemplate='Year: %{x}<br>Sales: %{y}<br>Category: %{legendgroup}<extra></extra>'
)


#térkép counties szerint

choropleth_data = zip_to_fip(df)

sales_min = choropleth_data['Sales'].min()
sales_max = choropleth_data['Sales'].max()
step = (sales_max - sales_min) / 5

tickvals = [round(sales_min + i * step, -2) for i in range(6)]
ticktext = [f"{int(val / 1000)}k" for val in tickvals]

fig6 = px.choropleth(
    choropleth_data,
    geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
    locations='FIPS',
    color='Sales',
    color_continuous_scale="twilight",
    range_color=(choropleth_data['Sales'].min(), choropleth_data['Sales'].max()),
    scope="usa",
    title="Sales by County",
)

fig6.update_layout(
    coloraxis_colorbar=dict(
        title="Sales",
        tickvals=tickvals,
        ticktext=ticktext,
        thickness=15,
        len=0.8,
    )
)



monthly_sales = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
monthly_sales['Order Date'] = monthly_sales['Order Date'].dt.to_timestamp()


fig10 = px.line(
    monthly_sales,
    x='Order Date',
    y='Sales',
    title='Monthly Sales Trends',
    labels={'Order Date': 'Month', 'Sales': 'Sales'},
    markers=True,
    line_shape='spline',
    color_discrete_sequence=px.colors.sequential.RdBu
)

fig10.update_traces(
    hovertemplate='Month: %{x|%b %Y}<br>Sales: %{y}<extra></extra>'
)


state_orders = df.groupby('State').size().reset_index(name='Order Count')
region_orders = df.groupby('Region').size().reset_index(name='Order Count')
state_region_orders = df.groupby(['Region', 'State']).size().reset_index(name='Order Count')


fig16 = px.pie(
    region_orders,
    names="Region",
    values="Order Count",
    title="Orders by Region",
    color_discrete_sequence=px.colors.sequential.RdBu)


fig17 = px.bar(
    state_region_orders,
    y="State",
    x="Order Count",
    color="Region",
    title="Orders by State and Region",
    barmode="group",
    orientation="h",
    color_continuous_scale=COLOR_SCALE
)

fig17.update_layout(
    bargap=0.1,
    bargroupgap=0.2
)

fig18 = px.treemap(
    state_region_orders,
    path=["Region", "State"],
    values="Order Count",
    title="Orders by Region and State",
    color="Order Count",
    color_continuous_scale=COLOR_SCALE
)

segment_category_distribution = (
    df.groupby(['Segment', 'Category'])['Order ID']
    .count()
    .reset_index(name='Order Count')
)

fig20 = px.bar(
    segment_category_distribution,
    x="Segment",
    y="Order Count",
    color="Category",
    title="Category Distribution by Segment",
    labels={"Order Count": "Order Count", "Segment": "Segment"},
    barmode="stack",
    color_continuous_scale=COLOR_SCALE)


segment_subcategory_distribution = (
    df.groupby(['Segment', 'Sub-Category'])['Order ID']
    .count()
    .reset_index(name='Order Count')
)

fig21 = px.bar(
    segment_subcategory_distribution,
    x="Segment",
    y="Order Count",
    color="Sub-Category",
    title="Sub-Category Distribution by Segment",
    labels={"Order Count": "Order Count", "Segment": "Segment"},
    barmode="stack",
    color_continuous_scale=COLOR_SCALE
)


subcategory_profit_distribution = (
    df.groupby('Sub-Category')['Profit']
    .sum()
    .reset_index()
)

fig23 = px.pie(
    subcategory_profit_distribution,
    names='Sub-Category',
    values='Profit',
    title='Profit Distribution by Sub-Category',
    color_discrete_sequence=px.colors.sequential.RdBu
)

category_order_distribution = (
    df.groupby('Category')['Order ID']
    .count()
    .reset_index(name='Order Count')
)

category_profit_distribution = (
    df.groupby('Category')['Profit']
    .sum()
    .reset_index()
)

category_colors = px.colors.sequential.RdBu
category_mapping = dict(zip(category_order_distribution['Category'].unique(), category_colors[:len(category_order_distribution)]))

fig24 = px.pie(
    category_order_distribution,
    names='Category',
    values='Order Count',
    title='Order Distribution by Category',
    color='Category',
    color_discrete_map=category_mapping
)

fig22 = px.pie(
    category_profit_distribution,
    names='Category',
    values='Profit',
    title='Profit Distribution by Category',
    color='Category',
    color_discrete_map=category_mapping
)


st.title('Superstore')

if menu == "Overview":
    col1, col2, col3 = st.columns(3)
    col1.metric(label='Total Sales', value=sales)
    col2.metric(label='Total Profit', value=profit)
    col3.metric(label='Number of Orders', value=orders)
    st.plotly_chart(fig3)

elif menu == "Top products":
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.plotly_chart(fig20)
    st.plotly_chart(fig21)
    st.plotly_chart(fig24)
    st.plotly_chart(fig22)
    st.plotly_chart(fig23)

elif menu == "Country statistics":
    st.plotly_chart(fig6)
    st.plotly_chart(fig16)
    st.plotly_chart(fig17)
    st.plotly_chart(fig18)

elif menu == "Trends":
    st.plotly_chart(fig4)
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig8)
    col2.plotly_chart(fig9)
    st.plotly_chart(fig10)