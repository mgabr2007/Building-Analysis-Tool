import streamlit as st
import pandas as pd
import openpyxl
import ifcopenshell
import matplotlib.pyplot as plt
from collections import defaultdict
import tempfile
import os

# Improved function to read Excel file with content-based caching
@st.cache(hash_funcs={bytes: hash})
def read_excel(file):
    wb = openpyxl.load_workbook(filename=file)
    sheet = wb.active
    data = sheet.values
    cols = next(data)[0:]
    df = pd.DataFrame(data, columns=cols)
    df = df.astype(str)
    return df

# Sidebar for navigation
st.sidebar.title("Analysis Options")
app_mode = st.sidebar.selectbox("Choose the type of analysis", ["IFC File Analysis", "Excel File Analysis"])

def ifc_analysis():
    st.title('IFC File Component Counter')
    uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'], key='ifc_uploader')

    if uploaded_file is not None:
        # Use a temporary file to securely handle the uploaded IFC file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as tmp_file:
            tmp_file_name = tmp_file.name
            tmp_file.write(uploaded_file.getvalue())
        
        try:
            ifc_file = ifcopenshell.open(tmp_file_name)
            st.write("File successfully uploaded and read. Counting building components:")

            component_count = count_building_components(ifc_file)

            # Display counts of components
            st.write("Counts of Building Components:")
            for component, count in component_count.items():
                st.write(f"{component}: {count}")

            # Visualize component count as a bar chart
            st.write("Bar Chart of Building Components:")
            fig_bar = visualize_component_count_bar_chart(component_count)
            st.pyplot(fig_bar)

            # Visualize component count as a pie chart
            st.write("Pie Chart of Building Components:")
            fig_pie = visualize_component_count_pie_chart(component_count)
            st.pyplot(fig_pie)
        except Exception as e:
            st.error(f"Error processing IFC file: {e}")
        finally:
            os.remove(tmp_file_name)

def excel_analysis():
    st.title('Excel Analyzer')
    file = st.file_uploader('Upload an Excel file', type=['xlsx'], key='excel_uploader')

    if file is not None:
        try:
            df = read_excel(file)

            st.write(f'Number of rows: {df.shape[0]}')
            st.write(f'Number of columns: {df.shape[1]}')

            st.write('Data:')
            st.dataframe(df)

            st.write('Basic analysis:')
            st.write(df.describe().to_string())
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")

# Render the selected app mode
if app_mode == "IFC File Analysis":
    ifc_analysis()
elif app_mode == "Excel File Analysis":
    excel_analysis()
