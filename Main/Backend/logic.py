import re

import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer


from Main.Backend import inputExtraction, loadData

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# List of words to ignore during the final frequency count tie-breaking
ignored_words = ['extruded', 'cooked', 'baked', 'red', 'green']

flag = True

# Function to tokenize and normalize words (using lemmatization)
def tokenize_and_normalize(sample_str, ignored_words=ignored_words):
    tokens = re.findall(r'\b\w+\b', sample_str.lower())
    if flag:
        tokens = [token for token in tokens if token not in ignored_words]
    # Normalize tokens using lemmatization
    normalized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return normalized_tokens

# Function to generate all consecutive word combinations (phrases) from a list of tokens
def generate_combinations(tokens):
    combinations = []
    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens) + 1):
            combinations.append(" ".join(tokens[i:j]))  # Join tokens to form phrases
    return combinations

# Function to find the best matching subcategory for a given sample string
def find_best_match(sample, data_file):
    sample_tokens = tokenize_and_normalize(sample)  # Normalize tokens
    flag = False  # Disable ignored words for further steps
    sample_combinations = generate_combinations(sample_tokens)
    best_matches = []
    max_matches = 0

    # Initial match calculation
    for category, subcategory_map in data_file.items():
        for subcategory, racc_value in subcategory_map.items():
            matches = sum(1 for comb in sample_combinations if comb in subcategory.lower())

            if matches > max_matches:
                best_matches = [(subcategory, racc_value)]
                max_matches = matches
            elif matches == max_matches:
                best_matches.append((subcategory, racc_value))

    # Sort by longest exact phrase match
    def exact_match_priority(subcat):
        subcat_tokens = tokenize_and_normalize(subcat)
        longest_match_length = max(
            (len(tokenize_and_normalize(comb)) for comb in sample_combinations if comb in subcat.lower()), default=0
        )
        return -longest_match_length

    if len(best_matches) > 1:
        best_matches.sort(key=lambda x: exact_match_priority(x[0]), reverse=True)

        # Check if there is still a tie after sorting by longest match
        if len(best_matches) > 1 and exact_match_priority(best_matches[0][0]) == exact_match_priority(best_matches[1][0]):
            def token_occurrence_count(subcat):
                subcat_tokens = tokenize_and_normalize(subcat)
                token_count = sum(subcat_tokens.count(token) for token in sample_tokens if token not in ignored_words)
                return token_count

            # Boosting logic for specific token matches
            def specific_match_boost(subcat):
                subcat_tokens = tokenize_and_normalize(subcat)
                return sum(1 for token in sample_tokens if token in subcat_tokens)

            best_match, best_racc_value = max(best_matches, key=lambda x: (specific_match_boost(x[0]), token_occurrence_count(x[0])))
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

def perform(file_path, json_path=None):
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
