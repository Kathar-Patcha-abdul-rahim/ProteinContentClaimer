import json


# Function to read JSON from a file and map categories to their sub-categories and RACC values
def load_json_and_map(path):
    # Read the JSON data from the file
    with open(path, 'r') as file:
        json_data = json.load(file)

    # Initialize an empty dictionary to hold the category-wise maps
    category_map = {}

    # Iterate over each food category in the JSON
    for food in json_data['foods']:
        category = food['Category']
        subcategories = food['sub-categories']
        racc_values = food['RACC-Value']

        # Create a dictionary mapping sub-categories to their RACC values
        subcategory_map = dict(zip(subcategories, racc_values))

        # Add the category and its subcategory map to the final dictionary
        category_map[category] = subcategory_map

    return category_map


# Path to your JSON file
file_path = '../resources/NutritionReferenceAmounts.json'

# Call the function and store the resulting dictionary
category_map = load_json_and_map(file_path)

# Print the resulting dictionary in the required format
for category, subcategory_map in category_map.items():
    # Print the category name
    print(f"Category: {category}")

    # Print each subcategory and its RACC value
    for subcategory, racc_value in subcategory_map.items():
        print(f"  {subcategory}: {racc_value}")

    # Print a blank line to separate categories
    print()
