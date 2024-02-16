import streamlit as st
import pandas as pd
import numpy as np
import ifcopenshell
import matplotlib.pyplot as plt
from collections import defaultdict
import tempfile
import os

# Function to count building components in an IFC file
def count_building_components(ifc_file):
    component_count = defaultdict(int)
    for ifc_entity in ifc_file.by_type('IfcProduct'):
        component_count[ifc_entity.is_a()] += 1
    return component_count

# Function to read Excel file with caching
@st.cache(hash_funcs={tempfile.NamedTemporaryFile: lambda _: None}, allow_output_mutation=True)
def read_excel(file):
    return pd.read_excel(file, engine='openpyxl')

# Unified visualization function for both bar and pie charts
def visualize_component_count(component_count, chart_type='bar'):
    labels, values = zip(*sorted(component_count.items(), key=lambda item: item[1], reverse=True))
    fig, ax = plt.subplots()
    if chart_type == 'bar':
        ax.bar(labels, values)
        plt.xticks(rotation=90)
    elif chart_type == 'pie':
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
    plt.tight_layout()
    return fig

def detailed_analysis(ifc_file, product_type, sort_by=None):
    product_count = defaultdict(int)
    for product in ifc_file.by_type(product_type):
        product_name = product.Name if product.Name else "Unnamed"
        type_name = product_name.split(':')[0] if product_name else "Unnamed"
        product_count[type_name] += 1

    labels, values = zip(*product_count.items()) if product_count else ((), ())
    if values:
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, counterclock=False)
        ax.axis('equal')
        plt.title(f"Distribution of {product_type} Products by Type")
        st.pyplot(fig)

        # Display sorted table if sort option is provided
        if sort_by:
            df = pd.DataFrame({'Type': labels, 'Count': values}).sort_values(by=sort_by, ascending=False)
            st.table(df)
    else:
        st.write(f"No products found for {product_type}.")

def ifc_file_analysis():
    uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'], key="ifc")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            ifc_file = ifcopenshell.open(tmp_file_path)
            component_count = count_building_components(ifc_file)
            chart_type = st.radio("Chart Type", ['bar', 'pie'], key="chart")
            fig = visualize_component_count(component_count, chart_type)
            st.pyplot(fig)

            if st.checkbox("Show Detailed Component Analysis", key="detailed"):
                product_types = sorted({entity.is_a() for entity in ifc_file.by_type('IfcProduct')})
                selected_product_type = st.selectbox("Select a product type for detailed analysis", product_types, key="product_type")
                sort_by = st.radio("Sort by", ["Type", "Count"], key="sort")
                detailed_analysis(ifc_file, selected_product_type, sort_by)
        finally:
            os.remove(tmp_file_path)

def excel_file_analysis():
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'], key="excel")
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist(), key="columns")
        if selected_columns:
            st.dataframe(df[selected_columns])
            visualize_data_button = st.button("Visualize Data", key="visualize")
            if visualize_data_button:
                visualize_data(df, selected_columns)
            generate_insights_button = st.button("Generate Insights", key="insights")
            if generate_insights_button:
                generate_insights(df[selected_columns])

def visualize_data(df, columns):
    for column in columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            fig, ax = plt.subplots()
            df[column].plot(kind='hist', ax=ax)
            plt.title(f"Histogram of {column}")
            st.pyplot(fig)
        else:
            fig, ax = plt.subplots()
            df[column].value_counts().plot(kind='bar', ax=ax)
            plt.title(f"Bar chart of {column}")
            st.pyplot(fig)

def generate_insights(df):
    if not df.empty:
        st.write("Descriptive Statistics:", df.describe())

def main():
    st.sidebar.title("Analysis Options")
    app_mode = st.sidebar.selectbox("Choose the type of analysis", ["IFC File Analysis", "Excel File Analysis"])

    if app_mode == "IFC File Analysis":
        ifc_file_analysis()
    elif app_mode == "Excel File Analysis":
        excel_file_analysis()

if __name__ == "__main__":
    main()
