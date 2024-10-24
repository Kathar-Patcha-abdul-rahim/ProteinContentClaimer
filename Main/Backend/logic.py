
import re

from Main.Backend import inputExtraction, loadData

# List of words to ignore during the final frequency count tie-breaking
ignored_words = ['extruded', 'cooked', 'baked']

# Function to convert a string into a list of words (tokens)
def tokenize_string(sample_str):
    return re.findall(r'\b\w+\b', sample_str.lower())

# Function to generate all consecutive word combinations (phrases) from a list of tokens
def generate_combinations(tokens):
    combinations = []
    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens) + 1):
            combinations.append(" ".join(tokens[i:j]))  # Join tokens to form phrases
    return combinations

# Function to find the best matching subcategory for a given sample string
def find_best_match(sample, data_file):
    sample_tokens = tokenize_string(sample)
    sample_combinations = generate_combinations(sample_tokens)
    best_matches = []
    max_matches = 0

    for category, subcategory_map in data_file.items():
        for subcategory, racc_value in subcategory_map.items():
            matches = sum(1 for comb in sample_combinations if comb in subcategory.lower())

            if matches > max_matches:
                best_matches = [(subcategory, racc_value)]
                max_matches = matches
            elif matches == max_matches:
                best_matches.append((subcategory, racc_value))

    print(f"List of best matches (before exact phrase check) for sample '{sample}':")
    for subcat, racc in best_matches:
        print(f" - Subcategory: {subcat}, RACC Value: {racc}")

    def exact_match_priority(subcat):
        subcat_tokens = tokenize_string(subcat)
        longest_match_length = max(
            (len(tokenize_string(comb)) for comb in sample_combinations if comb in subcat.lower()), default=0
        )
        return -longest_match_length

    if len(best_matches) > 1:
        best_matches.sort(key=lambda x: exact_match_priority(x[0]), reverse=True)

        if len(best_matches) > 1 and exact_match_priority(best_matches[0][0]) == exact_match_priority(best_matches[1][0]):
            def token_occurrence_count(subcat):
                subcat_tokens = tokenize_string(subcat)
                token_count = sum(subcat_tokens.count(token) for token in sample_tokens if token not in ignored_words)
                return token_count

            best_match, best_racc_value = max(best_matches, key=lambda x: token_occurrence_count(x[0]))
        else:
            best_match, best_racc_value = best_matches[0]
    else:
        best_match, best_racc_value = best_matches[0]

    return best_match, best_racc_value

def process_data(input_data, data_file):
    enhanced_data = []
    for row in input_data:
        sample_str = row['sample']
        best_match, racc_value = find_best_match(sample_str, data_file)

        enhanced_row = row.copy()
        enhanced_row['best_match'] = best_match
        enhanced_row['racc'] = racc_value

        enhanced_data.append(enhanced_row)

    print_results(enhanced_data)
    return enhanced_data

def print_results(enhanced_data):
    for i, row in enumerate(enhanced_data):
        print(f"S.No: {i + 1}")
        print(f"Sample: {row['sample']}")
        print(f"Best Matching Subcategory: {row['best_match']}")
        print(f"RACC Value: {row['racc']}\n")

def perform(file_path, json_path):
    df = inputExtraction.load_excel_file(file_path)
    columns_to_extract = ['SAMPLE', 'PROTEIN %', 'PDCAAS', 'IVPDCAAS']
    input_data = inputExtraction.extract_data(df, columns_to_extract)
    data_file = loadData.main(json_path)

    enhanced_data = process_data(input_data, data_file)

    return enhanced_data

def main():
    enhanced_data = perform("../SampleInputs/Pulse database for projects 4 .xlsx")
    return enhanced_data

if __name__ == "__main__":
    main()
