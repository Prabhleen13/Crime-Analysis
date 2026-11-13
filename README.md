# Crime Analysis

## Project Overview

Crime Analysis is a Python-based crime data analytics project built to explore and understand crime records through data cleaning, exploratory analysis, interactive dashboards, visualizations, and database connectivity.

The project uses a 40,160-record dataset with 17 fields. The supplied dataset includes report dates, occurrence dates and times, city, crime code and description, victim age and gender, weapon information, crime domain, police deployment, case closure information, occurrence period, and age group.

## Main Components

### 1. Data Cleaning (`data_cleaning.py`)
- Loads `crime_dataset_india.csv`.
- Inspects dataset dimensions, columns, data types, statistical summaries, missing values, duplicates, and category distributions.
- Validates victim age, police deployment, age groups, case status, and date relationships.
- Converts date columns into datetime format.
- Replaces missing weapon labels with `Not Recorded`.
- Saves the processed data as `crime_dataset_cleaned.csv`.

### 2. Interactive Dashboard (`crime_eda.py`)
The Streamlit dashboard connects to a MySQL database and reads records from the `crime_records` table. It provides analytical modules including:

- Overview
- Geography
- Time Patterns
- Victim Profiles
- Case Investigations
- Anomaly Detection
- Weapons & Deployment
- Analytics Lab
- Crime Forecasting
- Data Studio
- Data Quality
- City Profiles
- Comparative Analysis
- Homicide Review
- Summary Reports

The dashboard includes interactive charts, filters, data tables, analytical summaries, and CSV/PDF export features where implemented.

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Plotly
- MySQL Connector/Python
- SciPy
- Scikit-learn
- Statsmodels
- PyDeck
- ReportLab

## Repository Structure

```text
Crime-Analysis/
├── .streamlit/
│   └── secrets.toml.example
├── crime_dataset_india.csv
├── crime_dataset_cleaned.csv
├── crime_eda.py
├── data_cleaning.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Dataset Information

- Records: 40,160
- Columns: 17
- Original dataset: `crime_dataset_india.csv`
- Cleaned dataset: `crime_dataset_cleaned.csv`

The dataset is used for academic analysis and demonstration. Interpretations represent patterns in the supplied dataset and should not be treated as official real-time crime statistics or proof of causation.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Prabhleen13/Crime-Analysis.git
cd Crime-Analysis
```

### 2. Create and activate a virtual environment (recommended)

Windows PowerShell:

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure MySQL credentials locally

The dashboard reads from MySQL. The actual MySQL password and database name are deliberately not stored in this public repository.

Create a folder named `.streamlit` if it does not already exist. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, then enter your own local MySQL values in `secrets.toml`:

```toml
[mysql]
host = "localhost"
user = "root"
password = "ENTER_YOUR_LOCAL_MYSQL_PASSWORD"
database = "ENTER_YOUR_LOCAL_DATABASE_NAME"
```

Do not upload `.streamlit/secrets.toml` to GitHub. It is excluded by `.gitignore`.

The MySQL database must contain a table named `crime_records` with the 17 dataset fields in the same order expected by `crime_eda.py`. The database name is supplied privately through the local secrets file.

### 5. Run the data-cleaning script (optional)

Run this from the project folder:

```bash
python data_cleaning.py
```

It reads `crime_dataset_india.csv` and writes `crime_dataset_cleaned.csv`.

### 6. Run the dashboard

```bash
streamlit run crime_eda.py
```

Streamlit will provide a local URL in the terminal, usually `http://localhost:8501`.

## Important Notes

- The original project file is not modified by preparing this GitHub copy.
- The GitHub copy replaces hard-coded MySQL password and database-name values with local secrets/environment configuration.
- Keep your real `.streamlit/secrets.toml` private.
- Do not commit passwords, API keys, or private database configuration.
- The dashboard requires a reachable MySQL server and the expected `crime_records` table.
- The CSV files are included in this repository so the source and cleaned datasets are available alongside the code.

## Author

**Prabhleen Kaur**

MSc Information Technology Project
