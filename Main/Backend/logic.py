import inputExtraction
import loadData
import re

# Access variables from other files
inputData = inputExtraction.extracted_data
dataFile = loadData.category_map

# List of words to ignore during the final frequency count tie-breaking
ignored_words = ['extruded', 'cooked', 'baked']


# Function to convert a string into a list of words (tokens)
def tokenize_string(sample_str):
    # Using regex to extract words (split by space and special characters)
    return re.findall(r'\b\w+\b', sample_str.lower())


# Function to generate all consecutive word combinations (phrases) from a list of tokens
def generate_combinations(tokens):
    combinations = []
    # Generate combinations from n words to 1 word
    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens) + 1):
            combinations.append(" ".join(tokens[i:j]))  # Join tokens to form phrases
    return combinations


# Function to find the best matching subcategory for a given sample string
def find_best_match(sample, data_file):
    sample_tokens = tokenize_string(sample)  # Tokenize the sample string
    sample_combinations = generate_combinations(sample_tokens)  # Generate all word combinations
    best_matches = []  # List to hold multiple best matches if there's a tie
    max_matches = 0  # Highest number of matches
    original_sample_length = len(sample_tokens)  # Get word length of original sample

    # Iterate through each category and subcategory in dataFile
    for category, subcategory_map in data_file.items():
        for subcategory, racc_value in subcategory_map.items():
            # Count how many sample combinations are found in the subcategory
            matches = sum(1 for comb in sample_combinations if comb in subcategory.lower())

            # Check if this subcategory has more matches than the previous best
            if matches > max_matches:
                best_matches = [(subcategory, racc_value)]  # Start a new list of best matches
                max_matches = matches  # Update the max match count
            elif matches == max_matches:
                # If it's a tie, add this subcategory to the list of best matches
                best_matches.append((subcategory, racc_value))

    # Print the list of best matches before breaking the tie
    print(f"List of best matches (before exact phrase check) for sample '{sample}':")
    for subcat, racc in best_matches:
        print(f" - Subcategory: {subcat}, RACC Value: {racc}")

    # Prioritize the match that contains the longest exact match phrase from the input sample
    def exact_match_priority(subcat):
        subcat_tokens = tokenize_string(subcat)
        # Find the length of the longest exact match phrase between the sample and subcategory
        longest_match_length = max(
            (len(tokenize_string(comb)) for comb in sample_combinations if comb in subcat.lower()), default=0
        )
        return -longest_match_length  # Negative because we want to prioritize longer matches

    # If there's a tie after considering the longest exact phrase match, break it further
    if len(best_matches) > 1:
        # Break the tie based on longest exact match first
        best_matches.sort(key=lambda x: exact_match_priority(x[0]), reverse=True)

        # Check for remaining ties after sorting by longest exact match
        if len(best_matches) > 1 and exact_match_priority(best_matches[0][0]) == exact_match_priority(
                best_matches[1][0]):

            # Token occurrence frequency tie-breaker function (ignores specified words)
            def token_occurrence_count(subcat):
                subcat_tokens = tokenize_string(subcat)
                # Count occurrences of each token from the sample in the subcategory, ignoring specified words
                token_count = sum(subcat_tokens.count(token) for token in sample_tokens if token not in ignored_words)
                return token_count

            # Break tie by comparing token occurrence counts
            best_match, best_racc_value = max(best_matches, key=lambda x: token_occurrence_count(x[0]))
        else:
            best_match, best_racc_value = best_matches[0]  # No further tie, select the first one
    else:
        best_match, best_racc_value = best_matches[0]  # Only one best match, no tie to break

    return best_match, best_racc_value


# New variable to store input data along with the corresponding RACC values
enhanced_data = []

# Now, let's iterate over the inputData to find the best match for each sample
for row in inputData:
    sample_str = row['sample']  # Assuming 'sample' is the key in inputData
    best_match, racc_value = find_best_match(sample_str, dataFile)

    # Create a new dictionary containing all original fields plus the best match and RACC value
    enhanced_row = row.copy()  # Copy all fields from the original row
    enhanced_row['best_match'] = best_match  # Add the best match
    enhanced_row['racc'] = racc_value  # Add the RACC value

    # Add the enhanced row to the new data
    enhanced_data.append(enhanced_row)

# Print the enhanced data in the required format
for i, row in enumerate(enhanced_data):
    print(f"S.No: {i + 1}")
    print(f"Sample: {row['sample']}")
    print(f"Best Matching Subcategory: {row['best_match']}")
    print(f"RACC Value: {row['racc']}\n")

# Print the enhanced data to verify the contents
for i, row in enumerate(enhanced_data):
    print(f"Row {i + 1}: {row}")
