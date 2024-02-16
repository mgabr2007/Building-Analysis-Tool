import streamlit as st
import pandas as pd
from io import BytesIO
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
@st.cache(hash_funcs={BytesIO: lambda _: None}, allow_output_mutation=True)
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

def visualize_data(df, columns):
    for column in columns:
        st.subheader(f"Visualization for {column}")
        if pd.api.types.is_numeric_dtype(df[column]):
            # Histogram for numerical data
            fig, ax = plt.subplots()
            df[column].plot(kind='hist', ax=ax, bins=20)
            plt.xlabel(column)
            plt.ylabel("Frequency")
            st.pyplot(fig)
        else:
            # Bar chart for categorical data
            fig, ax = plt.subplots()
            df[column].value_counts().plot(kind='bar', ax=ax)
            plt.xticks(rotation=45)
            plt.xlabel(column)
            plt.ylabel("Count")
            st.pyplot(fig)

def main():
    st.sidebar.title("Analysis Options")
    app_mode = st.sidebar.selectbox("Choose the type of analysis", ["IFC File Analysis", "Excel File Analysis"])

    if app_mode == "IFC File Analysis":
        ifc_file_analysis()
    elif app_mode == "Excel File Analysis":
        excel_file_analysis()

def ifc_file_analysis():
    uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'])
    if uploaded_file is not None:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Open the IFC file using its temporary path
            ifc_file = ifcopenshell.open(tmp_file_path)
            component_count = count_building_components(ifc_file)
            chart_type = st.radio("Chart Type", ['bar', 'pie'])
            fig = visualize_component_count(component_count, chart_type)
            st.pyplot(fig)
        finally:
            # Clean up by removing the temporary file
            os.remove(tmp_file_path)

def excel_file_analysis():
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        
        # Allow user to select columns for analysis
        selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist())
        
        # Display the filtered dataframe with selected columns
        df_filtered = df[selected_columns]
        st.write(df_filtered)
        
        # Visualize selected data automatically
        visualize_data(df_filtered, selected_columns)

if __name__ == "__main__":
    main()
