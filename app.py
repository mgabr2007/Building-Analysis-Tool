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
        ax.pie(values, labels=labels, autopct=lambda p: '{:.1f}%'.format(p) if p > 0 else '', startangle=140)
        ax.axis('equal')
    plt.tight_layout()
    return fig

# Function to visualize data from Excel
def visualize_data(df, columns):
    chart_type = st.selectbox("Select chart type", ["Histogram", "Bar Chart"], index=0)
    for column in columns:
        if chart_type == "Histogram" and pd.api.types.is_numeric_dtype(df[column]):
            st.subheader(f"Histogram of {column}")
            fig, ax = plt.subplots()
            df[column].plot(kind='hist', ax=ax)
            plt.xlabel(column)
            st.pyplot(fig)
        elif chart_type == "Bar Chart" and not pd.api.types.is_numeric_dtype(df[column]):
            st.subheader(f"Bar Chart of {column}")
            fig, ax = plt.subplots()
            df[column].value_counts().plot(kind='bar', ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)

# Function for detailed analysis in IFC
def detailed_analysis(ifc_file, product_type, sort_by):
    product_count = defaultdict(int)
    for product in ifc_file.by_type(product_type):
        product_name = product.Name if product.Name else "Unnamed"
        type_name = product_name.split(':')[0] if product_name else "Unnamed"
        product_count[type_name] += 1

    total = sum(product_count.values())
    labels, values = zip(*product_count.items()) if product_count else ((), ())

    if values:
        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct=lambda p: '{:.1f}% ({}x)'.format(p, int(round(p * total / 100.0))) if p > 0 else '', startangle=90, counterclock=False)
        ax.axis('equal')
        plt.setp(autotexts, size=8, weight="bold")
        plt.title(f"Distribution of {product_type} Products by Type")
        st.pyplot(fig)

        data = {'Type': labels, 'Count': values}
        df = pd.DataFrame(data)
        if sort_by == "Name":
            df = df.sort_values('Type')
        elif sort_by == "Count":
            df = df.sort_values('Count', ascending=False)
        st.table(df)
    else:
        st.write(f"No products found for {product_type}.")

# IFC file analysis function
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
                sort_by = st.selectbox("Sort table by", ["Name", "Count"], index=1)
                detailed_analysis(ifc_file, selected_product_type, sort_by)
        finally:
            os.remove(tmp_file_path)

# Excel file analysis function
def excel_file_analysis():
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist())
        if selected_columns:
            df_filtered = df[selected_columns]
            st.dataframe(df_filtered)
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
