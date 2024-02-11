import streamlit as st
import pandas as pd
import openpyxl
import ifcopenshell
import matplotlib.pyplot as plt
from collections import defaultdict
import os
import plotly.graph_objects as go
import numpy as np

# Function to count building components in an IFC file
def count_building_components(ifc_file):
    component_count = defaultdict(int)
    for ifc_entity in ifc_file.by_type('IfcProduct'):
        entity_type = ifc_entity.is_a()
        component_count[entity_type] += 1
    return component_count

# Function to visualize the count of building components as a bar chart
def visualize_component_count_bar_chart(component_count):
    labels, values = zip(*sorted(component_count.items(), key=lambda item: item[1], reverse=True))
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_xlabel('Component Types')
    ax.set_ylabel('Count')
    ax.set_title('Count of Different Building Components')
    plt.xticks(rotation=90)
    plt.tight_layout()
    return fig

# Function to visualize the count of building components as a pie chart
def visualize_component_count_pie_chart(component_count):
    labels, sizes = zip(*component_count.items())
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    plt.tight_layout()
    return fig

# Function to read Excel file and return a Pandas DataFrame
@st.cache
def read_excel(file):
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    data = sheet.values
    cols = next(data)[0:]
    df = pd.DataFrame(data, columns=cols)
    df = df.astype(str)
    return df

# New function: Extract and visualize IFC geometry
def extract_and_visualize_ifc_geometry(ifc_file):
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)
    
    vertices = []  # List to hold vertices
    faces = []  # List to hold faces
    
    # Extract geometry for walls, doors, windows, and slabs
    for element in ifc_file.by_type('IfcWall') + ifc_file.by_type('IfcDoor') + ifc_file.by_type('IfcWindow') + ifc_file.by_type('IfcSlab'):
        shape = ifcopenshell.geom.create_shape(settings, element)
        verts = np.array(shape.geometry.verts).reshape((-1, 3))
        fcs = np.array(shape.geometry.faces).reshape((-1, 3))
        
        # Update vertices and faces lists
        vert_offset = len(vertices)
        vertices.extend(verts)
        faces.extend(fcs + vert_offset)
    
    return np.array(vertices), np.array(faces)

def plot_ifc_geometry(vertices, faces):
    fig = go.Figure(data=[go.Mesh3d(x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                                    i=faces[:,0], j=faces[:,1], k=faces[:,2],
                                    opacity=0.5)])
    fig.update_layout(scene=dict(aspectmode='data'))
    return fig

# Sidebar for navigation
st.sidebar.title("Analysis Options")
app_mode = st.sidebar.selectbox("Choose the type of analysis",
                                 ["IFC File Analysis", "Excel File Analysis", "IFC Geometry Visualization"])

# IFC Analysis Function
def ifc_analysis():
    st.title('IFC File Component Counter')
    uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'], key='ifc_uploader')

    if uploaded_file is not None:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        ifc_file = ifcopenshell.open(uploaded_file.name)
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

        # Clean up the uploaded file
        os.remove(uploaded_file.name)

# Excel Analysis Function
def excel_analysis():
    st.title('Excel Analyzer')
    st.write('Upload an Excel file to get started.')

    file = st.file_uploader('Upload an Excel file', type=['xlsx'], key='excel_uploader')

    if file is not None:
        df = read_excel(file)

        st.write(f'Number of rows: {df.shape[0]}')
        st.write(f'Number of columns: {df.shape[1]}')

        st.write('Data:')
        st.dataframe(df)

        st.write('Basic analysis:')
        st.write(df.describe().to_string())

# IFC Geometry Visualization Function
def ifc_geometry_visualization():
    st.title('IFC Geometry Visualization')
    uploaded_file = st.file_uploader("Choose an IFC file for geometry visualization", type=['ifc'], key='ifc_geom_uploader')

    if uploaded_file is not None:
        ifc_file = ifcopenshell.open(uploaded_file)
        vertices, faces = extract_and_visualize_ifc_geometry(ifc_file)
        fig = plot_ifc_geometry(vertices, faces)
        st.plotly_chart(fig)

# Render the selected app mode
if app_mode == "IFC File Analysis":
    ifc_analysis()
elif app_mode == "Excel File Analysis":
    excel_analysis()
elif app_mode == "IFC Geometry Visualization":
    ifc_geometry_visualization()
