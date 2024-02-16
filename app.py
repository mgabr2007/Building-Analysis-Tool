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
    chart_type = st.selectbox("Select chart type", ["Histogram", "Bar Chart"], index=0)
    if chart_type == "Histogram":
        for column in columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                st.subheader(f"Histogram of {column}")
                fig, ax = plt.subplots()
                df[column].plot(kind='hist', ax=ax)
                plt.xlabel(column)
                st.pyplot(fig)
            else:
                st.write(f"Note: {column} is not numeric and cannot be displayed as a histogram.")
    elif chart_type == "Bar Chart":
        for column in columns:
            if not pd.api.types.is_numeric_dtype(df[column]):
                st.subheader(f"Bar Chart of {column}")
                fig, ax = plt.subplots()
                df[column].value_counts().plot(kind='bar', ax=ax)
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.write(f"Note: {column} is numeric and better suited for histograms.")

def ifc_file_analysis():
    uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            ifc_file = ifcopenshell.open(tmp_file_path)
            component_count = count_building_components(ifc_file)
            chart_type = st.radio("Chart Type", ['bar', 'pie'])
            fig = visualize_component_count(component_count, chart_type)
            st.pyplot(fig)

            if st.checkbox("Show Detailed Component Analysis"):
                product_types = sorted({entity.is_a() for entity in ifc_file.by_type('IfcProduct')})
                selected_product_type = st.selectbox("Select a product type for detailed analysis", product_types)
                detailed_analysis(ifc_file, selected_product_type)

            if st.checkbox("Show Spatial Structure"):
                show_spatial_structure(ifc_file)
        finally:
            os.remove(tmp_file_path)

def detailed_analysis(ifc_file, product_type):
    components = ifc_file.by_type(product_type)
    st.write(f"Total number of {product_type}: {len(components)}")
    # Visualize with a pie chart
    if len(components) > 0:
        labels = [component.Name if component.Name else "Unnamed" for component in components[:10]]  # Limit to first 10 for clarity
        sizes = [1 for _ in components[:10]]  # Equal sizes just to show distribution
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1)
    else:
        st.write("No components found of this type.")

def show_spatial_structure(ifc_file):
    buildings = ifc_file.by_type('IfcBuilding')
    for building in buildings:
        st.write(f"Building: {building.Name}")
        storeys = building.IsDecomposedBy[0].RelatedObjects
        for storey in storeys:
            st.write(f"-- Storey: {storey.Name}")

def excel_file_analysis():
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist())
        df_filtered = df[selected_columns]
        st.write(df_filtered)
        
        if st.button("Visualize Selected Data"):
            visualize_data(df_filtered, selected_columns)

def main():
    st.sidebar.title("Analysis Options")
    app_mode = st.sidebar.selectbox("Choose the type of analysis", ["IFC File Analysis", "Excel File Analysis"])

    if app_mode == "IFC File Analysis":
        ifc_file_analysis()
    elif app_mode == "Excel File Analysis":
        excel_file_analysis()

if __name__ == "__main__":
    main()
