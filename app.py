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

def visualize_data(df, columns):
    """Visualize data from Excel."""
    for column in columns:
        st.write(f"Data Visualization for {column}")
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
    """Generate insights from the DataFrame."""
    if not df.empty:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_columns:
            st.write("Basic Statistical Insights")
            st.write(df[numeric_columns].describe())
        else:
            st.write("No numeric columns available for insights.")
    else:
        st.write("DataFrame is empty. No insights to display.")

def excel_file_analysis():
    """Analyze Excel files."""
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        if not df.empty:
            selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist())
            if selected_columns:
                st.dataframe(df[selected_columns])
                if st.button("Visualize Data"):
                    visualize_data(df, selected_columns)
                if st.button("Generate Insights"):
                    generate_insights(df[selected_columns])
        else:
            st.error("The uploaded Excel file is empty.")

def main():
    st.title("IFC and Excel File Analysis Tool")
    st.sidebar.title("Options")
    app_mode = st.sidebar.radio("Choose the type of analysis", ["Excel File Analysis"])

    if app_mode == "Excel File Analysis":
        excel_file_analysis()

if __name__ == "__main__":
    main()
