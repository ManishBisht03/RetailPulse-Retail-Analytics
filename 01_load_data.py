
from pathlib import Path

# Find the main RetailPulse project folder
project_folder = Path(__file__).resolve().parent.parent

# Find the dataset inside the data folder
data_folder = project_folder / "data"
file_path = data_folder / "online_retail_II.xlsx"

# Check whether the file exists
if file_path.exists():
    print("Success! RetailPulse found your Excel file.")
    print("File location:", file_path)
else:
    print("File not found. Please check the filename.")
    print("Expected location:", file_path)


import pandas as pd
from pathlib import Path

# Locate the RetailPulse project folder
project_folder = Path(__file__).resolve().parent.parent

# Locate the Excel dataset
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load the first worksheet
df = pd.read_excel(file_path, sheet_name=0)

# Display the first five rows
print("First 5 rows of RetailPulse data:")
print(df.head())

# Display the number of rows and columns
print("\nDataset shape:")
print(df.shape)

# Display the column names
print("\nColumn names:")
print(df.columns.tolist())


import pandas as pd
from pathlib import Path

# Locate the project and dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load the first worksheet
df = pd.read_excel(file_path, sheet_name=0)

# Count missing values in each column
print("Missing values in each column:")
print(df.isnull().sum())

# Calculate the total number of missing cells
print("\nTotal missing cells:")
print(df.isnull().sum().sum())

# Show the dataset size
print("\nDataset rows and columns:")
print(df.shape)


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load the first worksheet
df = pd.read_excel(file_path, sheet_name=0)

# Count duplicate rows
duplicate_count = df.duplicated().sum()

print("Total rows:", len(df))
print("Duplicate rows:", duplicate_count)

# Display duplicate rows for inspection
print("\nFirst duplicate records:")
print(df[df.duplicated()].head())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load the first worksheet
df = pd.read_excel(file_path, sheet_name=0)

# Check invalid quantities
print("Zero or negative quantities:")
print((df["Quantity"] <= 0).sum())

# Check invalid prices
print("\nZero or negative prices:")
print((df["Price"] <= 0).sum())

# Display sample records with invalid values
print("\nSample records with invalid quantities:")
print(df[df["Quantity"] <= 0].head())

print("\nSample records with invalid prices:")
print(df[df["Price"] <= 0].head())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load the first worksheet
df = pd.read_excel(file_path, sheet_name=0)

# Convert InvoiceDate into a date format
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

# Display the date range
print("Earliest transaction date:")
print(df["InvoiceDate"].min())

print("\nLatest transaction date:")
print(df["InvoiceDate"].max())

print("\nInvalid or missing dates:")
print(df["InvoiceDate"].isna().sum())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load the first worksheet
df = pd.read_excel(file_path, sheet_name=0)

# Count unique customers
unique_customers = df["Customer ID"].nunique()

# Count missing customer IDs
missing_customers = df["Customer ID"].isna().sum()

print("Total transactions:", len(df))
print("Unique customers:", unique_customers)
print("Rows with missing Customer IDs:", missing_customers)


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load the first worksheet
df = pd.read_excel(file_path, sheet_name=0)

# Check missing product descriptions
missing_descriptions = df["Description"].isna().sum()

# Count unique product codes
unique_products = df["StockCode"].nunique()

# Count missing product codes
missing_product_codes = df["StockCode"].isna().sum()

print("Total rows:", len(df))
print("Unique product codes:", unique_products)
print("Missing product descriptions:", missing_descriptions)
print("Missing product codes:", missing_product_codes)

# Display sample rows with missing descriptions
print("\nSample rows with missing descriptions:")
print(df[df["Description"].isna()].head())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load the first worksheet
df = pd.read_excel(file_path, sheet_name=0)

# Calculate sales value per row
df["Sales"] = df["Quantity"] * df["Price"]

# Calculate sales metrics
total_sales = df["Sales"].sum()
average_sales = df["Sales"].mean()

print("Total rows:", len(df))
print("Total sales value:", round(total_sales, 2))
print("Average sales value per row:", round(average_sales, 2))

print("\nFirst five rows with sales values:")
print(df[["Invoice", "StockCode", "Quantity", "Price", "Sales"]].head())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load both worksheets
sheets = pd.read_excel(file_path, sheet_name=None)

# Combine both worksheets into one dataset
df = pd.concat(sheets.values(), ignore_index=True)

# Display dataset information
print("Worksheets loaded:", list(sheets.keys()))
print("Total rows:", len(df))
print("Total columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst five rows:")
print(df.head())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load and combine both worksheets
sheets = pd.read_excel(file_path, sheet_name=None)
df = pd.concat(sheets.values(), ignore_index=True)

# Check missing values
print("Total rows:", len(df))
print("\nMissing values in each column:")
print(df.isnull().sum())

print("\nTotal missing cells:", df.isnull().sum().sum())

print("\nPercentage of missing values:")
print((df.isnull().mean() * 100).round(2))


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load and combine both worksheets
sheets = pd.read_excel(file_path, sheet_name=None)
df = pd.concat(sheets.values(), ignore_index=True)

# Count exact duplicate rows
duplicate_count = df.duplicated().sum()

print("Total rows:", len(df))
print("Exact duplicate rows:", duplicate_count)

# Display sample duplicate records
print("\nSample duplicate records:")
print(df[df.duplicated()].head())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load and combine both worksheets
sheets = pd.read_excel(file_path, sheet_name=None)
df = pd.concat(sheets.values(), ignore_index=True)

# Check invalid quantities and prices
invalid_quantities = (df["Quantity"] <= 0).sum()
invalid_prices = (df["Price"] <= 0).sum()

print("Total rows:", len(df))
print("Zero or negative quantities:", invalid_quantities)
print("Zero or negative prices:", invalid_prices)

# Display sample records for investigation
print("\nRows with zero or negative quantities:")
print(df[df["Quantity"] <= 0].head())

print("\nRows with zero or negative prices:")
print(df[df["Price"] <= 0].head())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load and combine both worksheets
sheets = pd.read_excel(file_path, sheet_name=None)
df = pd.concat(sheets.values(), ignore_index=True)

# Check customer IDs
missing_ids = df["Customer ID"].isna().sum()
unique_customers = df["Customer ID"].nunique()

print("Total transactions:", len(df))
print("Missing Customer IDs:", missing_ids)
print("Unique identified customers:", unique_customers)

# Show sample transactions without customer IDs
print("\nSample transactions with missing Customer IDs:")
print(df[df["Customer ID"].isna()].head())


import pandas as pd
from pathlib import Path

# Locate the dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "online_retail_II.xlsx"

# Load and combine both worksheets
sheets = pd.read_excel(file_path, sheet_name=None)
df = pd.concat(sheets.values(), ignore_index=True)

# Record original row count
original_rows = len(df)

# Remove exact duplicate rows
df = df.drop_duplicates()

# Remove rows missing essential fields
df = df.dropna(subset=["InvoiceDate", "StockCode"])

# Convert transaction dates to datetime
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

# Remove rows where date conversion failed
df = df.dropna(subset=["InvoiceDate"])

print("Original rows:", original_rows)
print("Rows after basic cleaning:", len(df))
print("Rows removed:", original_rows - len(df))
print("Remaining missing dates:", df["InvoiceDate"].isna().sum())
print("Remaining missing product codes:", df["StockCode"].isna().sum())


# Save the cleaned dataset

# Create the data folder if it does not exist
data_folder = Path(
    r"C:\Users\ASUS\OneDrive\Documents\RetailPulse-Analytics\data"
)
data_folder.mkdir(parents=True, exist_ok=True)


# Save the cleaned dataset inside the project data folder

from pathlib import Path

# Save the cleaned dataset outside OneDrive
output_folder = Path.home() / "RetailPulse_Test"
output_folder.mkdir(parents=True, exist_ok=True)

output_path = output_folder / "retailpulse_cleaned.csv"

df.to_csv(output_path, index=False)

print("CSV saved successfully!")
print("File location:", output_path)
print("File exists:", output_path.is_file())
