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
    # Initialize a dictionary to count instances of sub-types
    subtype_count = defaultdict(int)

    # Iterate through all instances of the selected component type
    for component in ifc_file.by_type(product_type):
        # Assume the subtype or a specific attribute is being used to differentiate instances
        subtype = getattr(component, 'PredefinedType', 'Undefined')
        subtype_count[subtype] += 1

    # Prepare data for pie chart
    labels, values = zip(*subtype_count.items())

    # Generate pie chart if there are subtypes to display
    if values:
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title(f"Distribution of {product_type} by Sub-Type")
        st.pyplot(fig)
    else:
        st.write("No subtypes found for the selected component.")

# Incorporate the detailed_analysis function into the ifc_file_analysis function as previously defined
# Ensure you also include the rest of the Streamlit app structure as shown in earlier examples

def main():
    # Streamlit app structure including the ifc_file_analysis function
    # as outlined in earlier examples

if __name__ == "__main__":
    main()
