import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import warnings
import plotly.figure_factory as ff
# os.getcwd for solve the problem read file and no such directory
os.getcwd()
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Sample Super Store EDA")
st.markdown('<style>div.block-container{padding-top: 2rem;}</style>', unsafe_allow_html=True)

file = st.file_uploader(":file_folder: Upload a file", type=(["csv","txt","xlsx","xls"]))
if file is not None:
    filename = file.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    os.chdir(r"C:\Users\MBlackPearl\NSLab\DataAnalytic\PythonDashboard\files")
    df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")

col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'])

StartDate = pd.to_datetime(df['Order Date']).min()
EndDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", StartDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", EndDate))

df = df[ (df['Order Date']>=date1)&(df['Order Date']<=date2) ].copy()

st.sidebar.header("Choose your filter : ")
region = st.sidebar.multiselect("Pick your Region", df['Region'].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]

state = st.sidebar.multiselect("Pick the State", df2['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]

city = st.sidebar.multiselect("Pick the City", df3['City'].unique())

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df = df[df['State'].isin(state)]
elif state and city:
    filtered_df = df3[df['State'].isin(state) & df3['City'].isin(city)]
elif region and city:
    filtered_df = df3[df['Region'].isin(region) & df3['City'].isin(city)]
elif region and state:
    filtered_df = df3[df['Region'].isin(region) & df3['State'].isin(state)]
elif city:
    filtered_df = df3[df3['City'].isin(city)]
else:
    filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]

category_df = filtered_df.groupby(by=['Category'], as_index=False)['Sales'].sum()
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df['Sales']],
        template="seaborn"
    )
    fig.update_traces(width=0.5)
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader('Region wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.6)
    fig.update_traces(text=filtered_df['Region'], textposition="outside")
    st.plotly_chart(fig, use_container_width=True, height=200)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download as CSV", data = csv, file_name="Category.csv", mime="text/csv",
            help="Click to download data as CSV file"
        )

with cl2:
    with st.expander("Region ViewData"):
        region_df = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download as CSV", data = csv, file_name="Region.csv", mime="text/csv",
            help="Click to download data as CSV file"
        )

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales" : "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Time Series : "):
    st.write(linechart.T.style.background_gradient(cmap='Blues'))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download as CSV", data=csv, file_name="TimeSerires.csv", mime="text/csv")

# create a tree map based on Region, Category & sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=['Region', 'Category', 'Sub-Category'], values="Sales", hover_data=['Sales'], color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

#create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1['layout'].update(
    title="Relationship between Sales and Profits using Scatter Plot", 
    xaxis=dict(title="Sales"),
    yaxis=dict(title="Profit")
)
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

#Download original dataset
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download as CSV", data=csv, file_name="Data.csv", mime="text/csv")