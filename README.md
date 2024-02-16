# IFC and Excel File Analysis Tool

This Streamlit application provides an interactive interface for analyzing IFC (Industry Foundation Classes) files and Excel spreadsheets. It allows users to visualize component counts in IFC files and perform data analysis and visualization on Excel files.

## Features

- **IFC File Analysis**: Upload IFC files to count and visualize different building components.
- **Excel File Analysis**: Upload Excel files to display data, visualize selected columns, and generate basic statistical insights.

## Installation

Before running the application, ensure you have Python installed on your system. This application requires Python 3.6 or later.

1. **Clone the Repository** (if applicable) or download the application code to your local machine.

2. **Create a Virtual Environment** (recommended):

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**:

   Install the required Python packages using the following command:

   ```bash
   pip install streamlit pandas numpy matplotlib ifcopenshell
   ```

## Usage

1. Navigate to the directory containing the application code in your terminal or command prompt.

2. Run the application using Streamlit:

   ```bash
   streamlit run app.py
   ```

3. The command will start the Streamlit server and open the application in your default web browser. If the application does not automatically open, you can manually navigate to the URL provided by Streamlit in the terminal output (typically `http://localhost:8501`).

4. Use the sidebar to select the type of analysis (IFC File Analysis or Excel File Analysis) and follow the on-screen instructions to upload files and visualize data.

## Customization

- **IFC Analysis**: Extend the `count_building_components` and `detailed_analysis` functions to include more detailed analysis of IFC files based on specific project requirements.
- **Excel Analysis**: Modify the `visualize_data` and `generate_insights` functions to include more advanced data visualization and insights generation techniques.

## Contributing

Contributions to improve the application are welcome. Please follow the standard fork-branch-PR workflow.

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Commit your changes.
4. Push the branch to your fork.
5. Submit a pull request.

## License

This project is licensed under the GNU General Public License (GPL). For more details, see the [LICENSE](LICENSE) file included with the project or visit the [GNU General Public License GPL](https://www.gnu.org/licenses/gpl-3.0.en.html) webpage.
