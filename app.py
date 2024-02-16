import streamlit as st
import pandas as pd
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

def detailed_analysis(ifc_file, product_type):
    subtype_count = defaultdict(int)
    for component in ifc_file.by_type(product_type):
        subtype = getattr(component, 'PredefinedType', 'Undefined')
        subtype_count[subtype] += 1
    labels, values = zip(*subtype_count.items()) if subtype_count else ((), ())
    if values:
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.title(f"Distribution of {product_type} by Sub-Type")
        st.pyplot(fig)
    else:
        st.write("No subtypes found for the selected component.")

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
        finally:
            os.remove(tmp_file_path)

def main():
    st.sidebar.title("Analysis Options")
    app_mode = st.sidebar.selectbox("Choose the type of analysis", ["IFC File Analysis", "Excel File Analysis"])

    if app_mode == "IFC File Analysis":
        ifc_file_analysis()
    # Include the rest of your Streamlit app logic here

if __name__ == "__main__":
    main()
