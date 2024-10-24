import json

from unicodedata import category


def load_json_file(path):
    """Load JSON data from a file."""
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file at {path} was not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
        return None


def map_subcategories_to_racc(json_data):
    """Map categories to their subcategories and RACC values."""
    category_map = {}

    for food in json_data.get('foods', []):
        category = food.get('Category')
        subcategories = food.get('sub-categories', [])
        racc_values = food.get('RACC-Value', [])

        # Create a dictionary mapping subcategories to their RACC values
        subcategory_map = dict(zip(subcategories, racc_values))

        # Add the category and its subcategory map to the final dictionary
        if category:
            category_map[category] = subcategory_map

    return category_map


def print_category_map(category_map):
    """Print the category map in a structured format."""
    for category, subcategory_map in category_map.items():
        print(f"Category: {category}")
        for subcategory, racc_value in subcategory_map.items():
            print(f"  {subcategory}: {racc_value}")
        print()  # Blank line to separate categories


def main(file_path = None):
    """Main function to load the JSON and print the category map."""
    category_map = []
    if file_path is None:
        file_path = '../resources/NutritionReferenceAmounts.json'
    json_data = load_json_file(file_path)

    if json_data:
        category_map = map_subcategories_to_racc(json_data)
        print_category_map(category_map)

    return category_map


if __name__ == "__main__":
    main()
