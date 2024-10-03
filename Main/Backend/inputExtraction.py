import pandas as pd

# Load the Excel file
file_path = '../SampleInputs/Pulse database for projects 4 .xlsx'  # Update this to your file path

# Read the Excel file into a pandas DataFrame
df = pd.read_excel(file_path)

# Select the required columns
columns_to_extract = ['SAMPLE', 'PROTEIN %', 'PDCAAS', 'IVPDCAAS']

# Create a list of dictionaries (key-value pairs) for each row, converting keys to lowercase
extracted_data = []

for _, row in df[columns_to_extract].iterrows():
    row_dict = {col.lower(): row[col] for col in df[columns_to_extract].columns}  # Convert keys to lowercase

    # Rename 'protein %' to 'protein'
    if 'protein %' in row_dict:
        row_dict['protein'] = row_dict.pop('protein %')

    extracted_data.append(row_dict)

# Now extracted_data is a list where each element is a dictionary with key-value pairs
# Example access to the first row
print(extracted_data[0])  # Access the first row (index 0)
print(extracted_data[1])  # Access the second row (index 1)

# To access the key-value pairs for each row in the list
for i, row in enumerate(extracted_data):
    print(f"Row {i}: {row}")
