"""Test script for spell correction functionality"""
import sys
import os

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.spell_correction import correct_query, suggest_corrections
from utils.validation import ValidationUtils

def test_spell_correction():
    """Test the spell correction functionality"""
    print("\n===== Testing Spell Correction =====\n")
    
    # Test cases with misspellings
    test_queries = [
        "what is my deductable amount",
        "does my policy cover preexisting conditions",
        "how long is the waiting peroid for maternity coverage",
        "what are the exclusions for knee surgury",
        "how do I file a cliam for hospitilization",
        "what are the benifits of my policy",
        "can I get a refund if I cancel my policy",
        "what is the copay for specialist visits",
        "how much is my premium for the next year",
        "what is the cancelation policy"
    ]
    
    # Test direct correction function
    print("Direct Spell Correction Results:")
    for query in test_queries:
        result = correct_query(query)
        if result["corrections_made"]:
            print(f"\nOriginal: {result['original_query']}")
            print(f"Corrected: {result['corrected_query']}")
            print("Corrections:")
            for correction in result["corrections"]:
                print(f"  - {correction['original']} → {correction['corrected']} ({correction['method']})")
        else:
            print(f"\nNo corrections needed for: {query}")
    
    # Test suggestion function
    print("\n\nSpell Correction Suggestions:")
    for query in test_queries[:3]:  # Just test first 3 queries
        suggestions = suggest_corrections(query)
        if suggestions:
            print(f"\nSuggestions for: {query}")
            for suggestion in suggestions:
                print(f"  - {suggestion['original']} → {suggestion['suggested']} "
                      f"(confidence: {suggestion['confidence']:.2f}, {suggestion['method']})")
        else:
            print(f"\nNo suggestions for: {query}")
    
    # Test integration with ValidationUtils
    print("\n\nValidation with Spell Correction:")
    validation_utils = ValidationUtils()
    for query in test_queries[:5]:  # Test first 5 queries
        validation_result = validation_utils.validate_query(query)
        print(f"\nQuery: {query}")
        print(f"Valid: {validation_result['valid']}")
        if validation_result["warnings"]:
            print("Warnings:")
            for warning in validation_result["warnings"]:
                print(f"  - {warning}")
        print(f"Cleaned query: {validation_result['cleaned_query']}")
        if "spell_corrections" in validation_result:
            print(f"Spell corrections applied: {len(validation_result['spell_corrections'])}")

if __name__ == "__main__":
    test_spell_correction()