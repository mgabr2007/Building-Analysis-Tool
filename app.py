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

# Function to read and cache Excel files
@st.cache(hash_funcs={tempfile.NamedTemporaryFile: lambda _: None}, allow_output_mutation=True)
def read_excel(file):
    return pd.read_excel(file, engine='openpyxl')

# Visualization for component counts (IFC and Excel)
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

# Generate insights for Excel data
def generate_insights(df):
    insights = []
    desc_stats = df.describe()
    for column in df.select_dtypes(include=[np.number]):
        insights.append(f"Mean of {column}: {desc_stats.at['mean', column]:.2f}")
        insights.append(f"Median of {column}: {desc_stats.at['50%', column]:.2f}")
        insights.append(f"Standard deviation of {column}: {desc_stats.at['std', column]:.2f}")
        skew = df[column].skew()
        if abs(skew) > 1:
            skewness = 'highly skewed'
        elif abs(skew) > 0.5:
            skewness = 'moderately skewed'
        else:
            skewness = 'approximately symmetric'
        insights.append(f"Distribution of {column} is {skewness} (skewness: {skew:.2f})")
        Q1 = desc_stats.at['25%', column]
        Q3 = desc_stats.at['75%', column]
        IQR = Q3 - Q1
        outlier_count = ((df[column] < (Q1 - 1.5 * IQR)) | (df[column] > (Q3 + 1.5 * IQR))).sum()
        insights.append(f"Potential outliers in {column}: {outlier_count}")
    if len(df.select_dtypes(include=[np.number]).columns) > 1:
        corr_matrix = df.corr()
        for index, value in corr_matrix.unstack().sort_values().iteritems():
            if value > 0.7 and value < 1:
                insights.append(f"{index[0]} and {index[1]} have a strong positive correlation (r: {value:.2f})")
            elif value < -0.7:
                insights.append(f"{index[0]} and {index[1]} have a strong negative correlation (r: {value:.2f})")
    return insights

# Detailed analysis for IFC files
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
    uploaded_file = st.file_uploader("Upload an Excel file for analysis", type=['xlsx'])
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        selected_columns = st.multiselect("Select columns to analyze", df.columns.tolist(), default=df.columns.tolist())
        if selected_columns:
            df_filtered = df[selected_columns]
            st.dataframe(df_filtered)
            if st.button("Visualize Selected Data"):
                visualize_data(df_filtered, selected_columns)
            if st.button("Generate Insights"):
                insights = generate_insights(df_filtered)
                for insight in insights:
                    st.info(insight)

def main():
    st.sidebar.title("Analysis Options")
    app_mode = st.sidebar.selectbox("Choose the type of analysis", ["IFC File Analysis", "Excel File Analysis"])
    if app_mode == "IFC File Analysis":
        ifc_file_analysis()
    elif app_mode == "Excel File Analysis":
        excel_file_analysis()

if __name__ == "__main__":
    main()
