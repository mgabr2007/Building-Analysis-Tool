import streamlit as st
import pandas as pd
from io import BytesIO
import ifcopenshell
import matplotlib.pyplot as plt
from collections import defaultdict

# Streamlined imports and using BytesIO for in-memory operations

# Enhanced Caching for Excel Reading
@st.cache(hash_funcs={BytesIO: lambda _: None}, allow_output_mutation=True)
def read_excel(file):
    return pd.read_excel(file, engine='openpyxl')

# Simplified Component Count Function
def count_building_components(ifc_file):
    component_count = defaultdict(int)
    for ifc_entity in ifc_file.by_type('IfcProduct'):
        component_count[ifc_entity.is_a()] += 1
    return component_count

# Unified Data Visualization Function
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

# Main App Functionality
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
        ifc_file = ifcopenshell.open(uploaded_file)
        component_count = count_building_components(ifc_file)
        chart_type = st.radio("Chart Type", ['bar', 'pie'])
        fig = visualize_component_count(component_count, chart_type)
        st.pyplot(fig)

def excel_file_analysis():
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        st.write(df)

if __name__ == "__main__":
    main()
