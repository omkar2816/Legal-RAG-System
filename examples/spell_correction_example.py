"""Example script demonstrating spell correction in API endpoints"""
import sys
import os
import json

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validation import ValidationUtils
from utils.spell_correction import correct_query, suggest_corrections

def simulate_api_endpoint(query: str):
    """Simulate an API endpoint with spell correction"""
    # Initialize validation utils
    validation_utils = ValidationUtils()
    
    # Step 1: Validate the query (includes spell correction)
    validation_result = validation_utils.validate_query(query)
    
    # Step 2: Check if the query is valid
    if not validation_result["valid"]:
        return {
            "status": "error",
            "errors": validation_result["errors"]
        }
    
    # Step 3: Process the query (in a real endpoint, this would search or generate an answer)
    # For this example, we'll just return the validation result with some mock data
    response = {
        "status": "success",
        "query": validation_result["cleaned_query"],
        "results": [
            {"id": 1, "title": "Sample Document 1", "snippet": "This is a sample result..."},
            {"id": 2, "title": "Sample Document 2", "snippet": "Another sample result..."}
        ]
    }
    
    # Step 4: Add query processing information if spell correction was applied
    if "original_query" in validation_result and "spell_corrections" in validation_result:
        response["query_processing"] = {
            "original_query": validation_result["original_query"],
            "processed_query": validation_result["cleaned_query"],
            "spell_corrections": validation_result["spell_corrections"],
            "corrections_applied": len(validation_result["spell_corrections"]) > 0
        }
    
    # Step 5: Add any warnings from validation
    if validation_result["warnings"]:
        response["warnings"] = validation_result["warnings"]
    
    return response

def main():
    """Run the example"""
    print("\n===== Spell Correction in API Endpoints Example =====\n")
    
    # Test queries with misspellings
    test_queries = [
        "what is my deductable amount",
        "does my policy cover preexisting conditions",
        "how long is the waiting peroid for maternity coverage",
        "what are the exclusions for knee surgury",
        "how do I file a cliam for hospitilization"
    ]
    
    for query in test_queries:
        print(f"\nProcessing query: '{query}'")
        response = simulate_api_endpoint(query)
        
        # Pretty print the response
        print("API Response:")
        print(json.dumps(response, indent=2))
        print("-" * 50)

if __name__ == "__main__":
    main()