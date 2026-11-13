
# ==========================================
# CRIME ANALYSIS PROJECT
# DATA CLEANING USING PYTHON
# ==========================================

# Step 1: Import required libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("Libraries imported successfully!")

# Step 2: Load the original dataset

df = pd.read_csv("crime_dataset_india.csv")

print("\nDataset loaded successfully!")

# Step 3: Display first five records

print("\nFIRST FIVE RECORDS")
print(df.head())

# Step 4: Display last five records

print("\nLAST FIVE RECORDS")
print(df.tail())

# Step 5: Check number of rows and columns

print("\nDATASET DIMENSIONS")
print(df.shape)

# Step 6: Check column names

print("\nCOLUMN NAMES")
print(df.columns)

# Step 7: Check data types and non-null values

print("\nDATASET INFORMATION")
df.info()

# Step 8: Statistical summary

print("\nSTATISTICAL SUMMARY")
print(df.describe(include="all"))

# ==========================================
# STEP 9: MISSING VALUE ANALYSIS
# ==========================================

print("\nMISSING VALUE ANALYSIS")

missing_values = df.isnull().sum()

missing_percentage = (missing_values / len(df)) * 100

missing_report = pd.DataFrame({
    "Missing Values": missing_values,
    "Missing Percentage": missing_percentage
})

print(missing_report[missing_report["Missing Values"] > 0])


# ==========================================
# STEP 10: DUPLICATE RECORD ANALYSIS
# ==========================================

print("\nDUPLICATE RECORD ANALYSIS")

print("Total duplicate rows:", df.duplicated().sum())

print("Duplicate Report Numbers:",
      df["Report Number"].duplicated().sum())


# ==========================================
# STEP 11: UNIQUE VALUE ANALYSIS
# ==========================================

print("\nUNIQUE VALUES IN CATEGORICAL COLUMNS")

categorical_columns = df.select_dtypes(include="object").columns

for column in categorical_columns:
    print("\n", column)
    print(df[column].value_counts(dropna=False))


# ==========================================
# STEP 12: NUMERIC VALUE VALIDATION
# ==========================================

print("\nNUMERIC COLUMN VALIDATION")

print("Minimum Victim Age:", df["Victim Age"].min())
print("Maximum Victim Age:", df["Victim Age"].max())

print("Minimum Police Deployed:", df["Police Deployed"].min())
print("Maximum Police Deployed:", df["Police Deployed"].max())


# ==========================================
# STEP 13: CASE STATUS CONSISTENCY
# ==========================================

print("\nCASE STATUS COMPARISON")

print(pd.crosstab(df["Case Status"], df["Case Closed"]))


print("\nINITIAL DATA QUALITY INSPECTION COMPLETED")

# ==========================================
# STEP 14: AGE GROUP VALIDATION
# ==========================================

print("\nAGE GROUP VALIDATION")

print(pd.crosstab(
    df["Victim Age"],
    df["Age Group"]
))

# Check age ranges associated with each age group

print("\nAGE RANGE BY AGE GROUP")

print(
    df.groupby("Age Group")["Victim Age"]
      .agg(["min", "max", "mean", "count"])
)


# ==========================================
# STEP 15: CASE DATE VALIDATION
# ==========================================

print("\nCASE DATE VALIDATION")

# Convert dates into datetime format for checking

occurrence_date = pd.to_datetime(
    df["Date of Occurance"],
    format="%d %B %Y",
    errors="coerce"
)

reported_date = pd.to_datetime(
    df["Date Reported"],
    format="%d %B %Y",
    errors="coerce"
)

closure_date = pd.to_datetime(
    df["Date and Time of Case Closed"],
    format="%d-%m-%Y %H:%M",
    errors="coerce"
)

# Check if reporting date is earlier than occurrence date

print(
    "\nReports dated before occurrence:",
    (reported_date < occurrence_date).sum()
)

# Check if closure date is earlier than occurrence date

print(
    "\nCases closed before occurrence:",
    (closure_date.dt.normalize() < occurrence_date).sum()
)

# Check if closure date is earlier than reporting date

print(
    "\nCases closed before reporting:",
    (closure_date.dt.normalize() < reported_date).sum()
)


# ==========================================
# STEP 16: CASE STATUS AND DATE CONSISTENCY
# ==========================================

print("\nCASE DATE AND STATUS CHECK")

print(pd.crosstab(
    df["Case Status"],
    closure_date.notna()
))


print("\nAGE AND DATE VALIDATION COMPLETED")

# STEP 17: CREATE A WORKING COPY
clean_df = df.copy()

# STEP 18: CONVERT DATE COLUMNS INTO DATETIME FORMAT
clean_df["Date Reported"] = pd.to_datetime(
    clean_df["Date Reported"],
    format="%d %B %Y",
    errors="coerce"
)

clean_df["Date of Occurance"] = pd.to_datetime(
    clean_df["Date of Occurance"],
    format="%d %B %Y",
    errors="coerce"
)

clean_df["Date and Time of Case Closed"] = pd.to_datetime(
    clean_df["Date and Time of Case Closed"],
    format="%d-%m-%Y %H:%M",
    errors="coerce"
)

# STEP 19: CHECK DATE CONVERSION
print("\nDATE CONVERSION CHECK")
print(clean_df[[
    "Date Reported",
    "Date of Occurance",
    "Date and Time of Case Closed"
]].dtypes)

print("\nDATE CONVERSION MISSING VALUES")
print(clean_df[[
    "Date Reported",
    "Date of Occurance",
    "Date and Time of Case Closed"
]].isnull().sum())

print("\nDATE CONVERSION COMPLETED")

# STEP 20: HANDLE MISSING WEAPON INFORMATION

print("\nMISSING VALUES BEFORE CLEANING")
print(clean_df.isnull().sum())

clean_df["Weapon Used"] = clean_df["Weapon Used"].fillna("Not Recorded")

print("\nMISSING VALUES AFTER CLEANING")
print(clean_df.isnull().sum())

print("\nWEAPON CATEGORY DISTRIBUTION")
print(clean_df["Weapon Used"].value_counts())

print("\nMISSING VALUE HANDLING COMPLETED")

# STEP 21: SAVE THE CLEANED DATASET

clean_df.to_csv("crime_dataset_cleaned.csv", index=False)

print("\nCLEANED DATASET SAVED SUCCESSFULLY!")

# STEP 22: VERIFY THE SAVED DATASET
verified_df = pd.read_csv("crime_dataset_cleaned.csv")

print("\nSAVED DATASET DIMENSIONS:")
print(verified_df.shape)

print("\nSAVED DATASET MISSING VALUES:")
print(verified_df.isnull().sum())

print("\nCLEANED DATASET VERIFICATION COMPLETED")
# STEP 23: EXPLORATORY DATA ANALYSIS (EDA)

print("\nCRIME DISTRIBUTION ACROSS CITIES")

city_crimes = clean_df["City"].value_counts()

print(city_crimes)



