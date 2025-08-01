#!/usr/bin/env python3
"""
Test script to verify the metadata builder fix
"""
from chunking.metadata_builder import metadata_builder

def test_metadata_fix():
    """Test that legal_terms is now a list of strings"""
    print("Testing metadata builder fix...")
    
    # Test text with legal terms
    test_text = "This agreement is entered into by the parties. The contract contains terms and conditions."
    
    # Get legal analysis
    analysis = metadata_builder._analyze_legal_terms(test_text)
    
    print(f"Legal terms type: {type(analysis['legal_terms'])}")
    print(f"Legal terms value: {analysis['legal_terms']}")
    
    # Check if it's a list
    if isinstance(analysis['legal_terms'], list):
        print("✅ SUCCESS: legal_terms is now a list of strings")
        print(f"List length: {len(analysis['legal_terms'])}")
        print(f"Sample terms: {analysis['legal_terms'][:5] if analysis['legal_terms'] else 'None'}")
    else:
        print("❌ FAILURE: legal_terms is still not a list")
        print(f"Type: {type(analysis['legal_terms'])}")
    
    # Test with more legal terms
    complex_text = """
    WHEREAS, the parties desire to enter into this agreement;
    NOW, THEREFORE, in consideration of the mutual promises and covenants contained herein, 
    the parties agree as follows:
    
    ARTICLE I: EMPLOYMENT
    Section 1.1: Position and Duties
    The Company hereby employs the Employee as Senior Software Engineer.
    
    ARTICLE II: CONFIDENTIALITY
    The Employee acknowledges that during employment, the Employee will have access to 
    confidential and proprietary information of the Company.
    """
    
    analysis2 = metadata_builder._analyze_legal_terms(complex_text)
    print(f"\nComplex text legal terms: {analysis2['legal_terms']}")
    print(f"Legal term count: {analysis2['legal_term_count']}")
    print(f"Legal density: {analysis2['legal_density']:.3f}")

if __name__ == "__main__":
    test_metadata_fix() 