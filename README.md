# Educational Data Analysis Tool

## Overview
This application analyzes student activity logs to track engagement across different components (Course, Quiz, Assignment, etc.). It processes CSV files containing activity data and generates visualizations and statistical analysis.

## Prerequisites
- Anaconda Distribution (Python 3.8 or higher)
- At least 4GB RAM
- Windows 10 or higher

## Installation

### 1. Setting Up the Environment
```bash
# Create the conda environment
conda env create -f environment.yml

# Activate the environment
conda activate advprog_app
```

### 2. Verifying Installation
To verify your installation:
```bash
python verify_env.py
```
This will show all installed packages and their versions.

## Usage

### 1. Data Files
Place your CSV files in the `data` folder:
- ACTIVITY_LOG.csv (student activity records)
- USER_LOG.csv (user timestamps)
- COMPONENT_CODES.csv (component reference data)

### 2. Running the Application
```bash
# Ensure uni_logs environment is activated
conda activate advprog_app

# Launch the application
python src/gui.py
```

### 3. Using the Interface

The application interface has several sections:

a) Data Loading:
- Click "Load CSV Files" to import your data files
- Select all three required CSV files when prompted

b) Data Processing:
1. Process CSV - Initial data processing
2. Remove Excluded Components - Filter out system components
3. Rename Columns - Standardize column names
4. Merge Datasets - Combine all data
5. Reshape Data - Transform for analysis
6. Count Interactions - Calculate engagement metrics
7. Save All Data to Excel - Export results

c) Analysis Options:
- Interaction Heatmap
- User Timeline
- Component Distribution
- Monthly Trends
- User Activity Patterns
- Component Correlations
- Usage Pattern Clusters

### 4. Viewing Results
- Results are displayed in the application tabs
- Exported Excel files are saved in the files folder

## Troubleshooting

Common Issues:
1. "conda command not found"
   - Add Anaconda to your system PATH
   - Or use Anaconda Prompt directly

2. "Module not found" errors
   - Ensure advprog_app environment is activated
   - Verify environment creation was successful

3. Data loading errors
   - Check CSV file formatting
   - Ensure files are in the correct location

## Project Structure
```
Uni_ActivityLogs_App/
├── datasets/                  # Input data files
├── src/                   # Source code
│   ├── gui.py            # Main application interface
│   └── data_storage.py   # Data processing logic
├── environment.yml        # Conda environment file
├── requirements.txt       # Pip requirements file
└── README.md             # This file
```

## Contributing
This is a university project for the Advanced Programming module. Please contact the maintainer for any questions.

## Author
Kevin Deffogang
MSc Computer Science
University of York

## Version
1.0.0 - Initial Release

## License
For educational use only.

## Acknowledgments
- University of York Computing Department
