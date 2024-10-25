from Main.Backend import logic


def convert_if_percentage(value):
    """Convert a percentage value to a normal value if it's greater than 1."""
    if value > 1:  # Assuming values greater than 1 are percentages
        return value / 100
    return value


def calculate_pdcaas_claim(protein, racc, pdcaas, ivpdcaas):
    """Perform PDCAAS and IVPDCAAS claim calculations."""
    pdcaas_claim = (protein / 100) * pdcaas * (racc / 100)
    ivpdcaas_claim = (protein / 100) * ivpdcaas * (racc / 100)

    return pdcaas_claim, ivpdcaas_claim


def determine_claim(claim):
    """Determine the claim classification based on the calculated claim value."""
    if claim < 5:
        return "No claim"
    elif 5 <= claim < 10:
        return "Good source"
    elif claim >= 10:
        return "Excellent source"
    return "Unknown claim"


def process_enhanced_data(enhanced_data):
    """Process each entry in the enhanced data to calculate claims and classifications."""
    for entry in enhanced_data:
        # Extract relevant values from the entry
        protein = entry['protein']
        racc = entry['racc']
        pdcaas = entry['pdcaas']
        ivpdcaas = entry['ivpdcaas']

        # Perform the calculations
        pdcaas_claim, ivpdcaas_claim = calculate_pdcaas_claim(protein, racc, pdcaas, ivpdcaas)

        # Determine claim classification
        pdcaas_claim_status = determine_claim(pdcaas_claim)
        ivpdcaas_claim_status = determine_claim(ivpdcaas_claim)

        # Add results to the entry
        entry['pdcaas_claim'] = pdcaas_claim
        entry['ivpdcaas_claim'] = ivpdcaas_claim
        entry['pdcaas_claim_status'] = pdcaas_claim_status
        entry['ivpdcaas_claim_status'] = ivpdcaas_claim_status

    display_results(enhanced_data)
    return enhanced_data


def display_results(enhanced_data):
    """Display the results for each entry in a structured format."""
    for entry in enhanced_data:
        print(f"Sample: {entry['sample']}")
        print(f"Best Match: {entry.get('best_match', 'N/A')}")
        print(f"Protein: {entry['protein']}g")
        print(f"RACC: {entry['racc']}g")
        print(f"PDCAAS: {entry['pdcaas']} -> Claim: {entry['pdcaas_claim']} ({entry['pdcaas_claim_status']})")
        print(f"IVPDCAAS: {entry['ivpdcaas']} -> Claim: {entry['ivpdcaas_claim']} ({entry['ivpdcaas_claim_status']})")
        print()  # Print a blank line for better readability


def perform_operation(file_path=None, json_path=None):
    # Set default file path if no file path is provided
    if file_path is None:
        file_path = "../SampleInputs/Pulse database for projects 4 .xlsx"

    # Retrieve enhanced data from the logic module
    enhanced_data = logic.perform(file_path, json_path)

    # Process and display the enhanced data
    process_enhanced_data(enhanced_data)

    display_results(enhanced_data)
    return enhanced_data


def main(file_path=None):
    # Call perform with the given file_path or default
    enhanced_data = perform_operation(file_path)

    # Display results from the processed enhanced data
    display_results(enhanced_data)


if __name__ == "__main__":
    main()
