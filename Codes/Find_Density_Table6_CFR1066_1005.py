import json

def find_chemical_species_density(keyword, json_filename):
    """
    Reads a JSON file and returns entries where the 'Symbol' 
    contains the specified keyword.
    """
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter entries where the keyword is in the 'Symbol' field
        matches = [entry for entry in data if keyword in entry.get("Symbol", "")]
        return matches
    except FileNotFoundError:
        return f"Error: The file '{json_filename}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"

# Configuration
filename = "json/Table6_CFR1066_1005.json"
search_keyword = "NOx"

# Execute the search
results = find_chemical_species_density(search_keyword, filename)

# Display the results
if isinstance(results, list) and results:
    print(f"Results for keyword '{search_keyword}':\n")
    for row in results:
        print(f"Symbol:   {row.get('Symbol')}")
        print(f"Quantity: {row.get('Quantity')}")
        print(f"g/m³:     {row.get('g_per_m3')}")
        print(f"g/ft³:    {row.get('g_per_ft3')}")
        print("-" * 30)
else:
    print(f"No species found with keyword '{search_keyword}'.")

# import pandas as pd
# import json

# # Method 1: Using Pandas (Recommended for DataFrames)
# def find_nox_with_pandas(file_path):
#     df = pd.read_json(file_path)
#     # Filter rows where 'Symbol' contains 'NOx'
#     nox_data = df[df['Symbol'].str.contains("NOx", case=False)]
#     return nox_data[['Symbol', 'g_per_m3', 'g_per_ft3']]

# # Method 2: Using the built-in json library
# def find_nox_with_json(file_path):
#     with open(file_path, 'r') as f:
#         data = json.load(f)
    
#     results = []
#     for item in data:
#         if "NOx" in item['Symbol']:
#             results.append({
#                 "Symbol": item['Symbol'],
#                 "g_per_m3": item['g_per_m3'],
#                 "g_per_ft3": item['g_per_ft3']
#             })
#     return results

# # Execution
# file_name = "Table6_CFR1066_1005.json"

# print("--- Results using Pandas ---")
# print(find_nox_with_pandas(file_name))

# print("\n--- Results using JSON library ---")
# print(find_nox_with_json(file_name))