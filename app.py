import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import tempfile
import os
import ifcopenshell

def read_excel(file):
    """Read and return the Excel file."""
    return pd.read_excel(file, engine='openpyxl')

def count_building_components(ifc_file):
    """Count components in an IFC file."""
    component_count = defaultdict(int)
    for ifc_entity in ifc_file.by_type('IfcProduct'):
        component_count[ifc_entity.is_a()] += 1
    return component_count

def visualize_component_count(component_count, chart_type='bar'):
    """Visualize component count for IFC files."""
    labels, values = zip(*sorted(component_count.items(), key=lambda item: item[1], reverse=True))
    fig, ax = plt.subplots()
    if chart_type == 'bar':
        ax.bar(labels, values)
        plt.xticks(rotation=90)
    elif chart_type == 'pie':
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
    plt.tight_layout()
    st.pyplot(fig)

def visualize_data(df, columns):
    """Visualize data from Excel files."""
    for column in columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            fig, ax = plt.subplots()
            df[column].hist(ax=ax)
            ax.set_title(column)
            st.pyplot(fig)
        else:
            fig, ax = plt.subplots()
            df[column].value_counts().plot(kind='bar', ax=ax)
            ax.set_title(column)
            st.pyplot(fig)

def generate_insights(df):
    """Generate insights from Excel data."""
    if not df.empty:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_columns:
            st.write("Basic Statistical Insights")
            st.write(df[numeric_columns].describe())
        else:
            st.write("No numeric columns available for insights.")
    else:
        st.write("DataFrame is empty. No insights to display.")

def ifc_file_analysis():
    """Analyze IFC files."""
    uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'], key="ifc_uploader")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as tmp_file:
            tmp_file.write(uploaded_file.read())
            ifc_file = ifcopenshell.open(tmp_file.name)
        component_count = count_building_components(ifc_file)
        chart_type = st.selectbox("Select chart type", ['bar', 'pie'], key="chart_type_select")
        visualize_component_count(component_count, chart_type)

def excel_file_analysis():
    """Analyze Excel files."""
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'], key="excel_uploader")
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        if not df.empty:
            selected_columns = st.multiselect("Select columns to analyze", df.columns.tolist(), default=df.columns.tolist(), key="columns_select")
            if selected_columns:
                st.dataframe(df[selected_columns])
                if st.button("Visualize Data", key="visualize_button"):
                    visualize_data(df, selected_columns)
                if st.button("Generate Insights", key="generate_insights_button"):
                    generate_insights(df[selected_columns])
        else:
            st.error("The uploaded Excel file is empty.")

def main():
    st.title("IFC and Excel File Analysis Tool")
    st.sidebar.title("Options")
    app_mode = st.sidebar.radio("Choose the type of analysis", ["IFC File Analysis", "Excel File Analysis"])

    if app_mode == "IFC File Analysis":
        ifc_file_analysis()
    elif app_mode == "Excel File Analysis":
        excel_file_analysis()

if __name__ == "__main__":
    main()
