import logic

enhanced_data = logic.enhanced_data

# Function to check if the value is in percentage and convert it to a normal value
def convert_if_percentage(value):
    if value > 1:  # Assuming values greater than 1 are percentages
        return value / 100
    return value

# Function to perform PDCAAS claim calculation
def calculate_pdcaas_claim(protein, racc, pdcaas, ivpdcaas):
    # Formula for calculation (PDCAAS and IVPDCAAS):
    pdcaas_claim = (protein / 100) * pdcaas * (racc / 100)
    ivpdcaas_claim = (protein / 100) * ivpdcaas * (racc / 100)

    return pdcaas_claim, ivpdcaas_claim

# Function to determine claim classification
def determine_claim(claim):
    if claim < 5:
        return "No claim"
    elif 5 <= claim < 10:
        return "Good source"
    elif claim >= 10:
        return "Excellent source"
    return "Unknown claim"

# Loop through each entry in enhanced_data
for entry in enhanced_data:
    # Extracting relevant values from the entry
    protein = entry['protein']
    racc = entry['racc']
    pdcaas = entry['pdcaas']
    ivpdcaas = entry['ivpdcaas']

    # Perform the calculations
    pdcaas_claim, ivpdcaas_claim = calculate_pdcaas_claim(protein, racc, pdcaas, ivpdcaas)

    # Determine claim classification
    pdcaas_claim_status = determine_claim(pdcaas_claim)
    ivpdcaas_claim_status = determine_claim(ivpdcaas_claim)

    # Display the results for the current entry
    print(f"Sample: {entry['sample']}")
    print(f"Best Match: {entry['best_match']}")
    print(f"Protein: {protein}g")
    print(f"RACC: {racc}g")
    print(f"PDCAAS: {pdcaas} -> Claim: {pdcaas_claim} ({pdcaas_claim_status})")
    print(f"IVPDCAAS: {ivpdcaas} -> Claim: {ivpdcaas_claim} ({ivpdcaas_claim_status})")
    print()  # Print a blank line for better readability
