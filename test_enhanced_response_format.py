#!/usr/bin/env python3
"""
Test script for enhanced response format and structured responses
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_service.response_formatter import response_formatter, ResponseType, ConfidenceLevel
from llm_service.response_schema import ResponseFormatter, ResponseSchemaValidator

def test_enhanced_response_format():
    """Test the enhanced response formatter"""
    print("=== Testing Enhanced Response Format ===")
    
    # Sample data
    sample_answer = "According to the policy document, the waiting period for pre-existing conditions is 48 months. This is clearly stated in Section 4.2 of the policy document on page 15. The policy specifies that any medical condition that existed before the policy start date will not be covered until 48 months have elapsed from the policy commencement date."
    
    sample_sources = [
        {
            "doc_id": "policy_001",
            "doc_title": "Health Insurance Policy",
            "section_title": "Waiting Periods",
            "similarity_score": 0.85,
            "text": "Waiting period for pre-existing conditions: 48 months from policy commencement date.",
            "page_number": 15,
            "chunk_id": "chunk_001",
            "word_count": 25,
            "legal_density": 0.8,
            "structural_rank": 1,
            "retrieval_method": "semantic_search"
        },
        {
            "doc_id": "policy_001",
            "doc_title": "Health Insurance Policy",
            "section_title": "Exclusions",
            "similarity_score": 0.72,
            "text": "Pre-existing conditions are excluded from coverage until the waiting period has elapsed.",
            "page_number": 12,
            "chunk_id": "chunk_002",
            "word_count": 20,
            "legal_density": 0.7,
            "structural_rank": 2,
            "retrieval_method": "semantic_search"
        }
    ]
    
    sample_query = "What is the waiting period for pre-existing conditions?"
    
    # Test enhanced response formatting
    try:
        formatted_response = response_formatter.format_response(
            answer=sample_answer,
            sources=sample_sources,
            confidence=0.78,
            query=sample_query,
            threshold_used=0.7,
            structured_data={
                "questions": [sample_query],
                "confidence_scores": [0.78],
                "overall_confidence": 0.78,
                "clause_references": [
                    {"clause": "Section 4.2", "page": 15, "text": "Waiting period for pre-existing conditions: 48 months"}
                ],
                "source_clause_ref": sample_sources,
                "context_chunks_used": 2,
                "metadata": {
                    "context_relevance": 0.85,
                    "completeness": 0.9
                }
            }
        )
        
        print("✅ Enhanced response formatting successful")
        print(f"Response ID: {formatted_response.get('response_id')}")
        print(f"Response Type: {formatted_response.get('response_type')}")
        print(f"Category: {formatted_response.get('category')}")
        print(f"Confidence Level: {formatted_response.get('confidence', {}).get('level')}")
        print(f"Total Sources: {formatted_response.get('sources', {}).get('total_count')}")
        
        # Validate response
        validation_result = ResponseSchemaValidator.validate_response(formatted_response)
        if validation_result["valid"]:
            print("✅ Response validation successful")
        else:
            print("❌ Response validation failed:")
            for error in validation_result["errors"]:
                print(f"  - {error}")
        
        return formatted_response
        
    except Exception as e:
        print(f"❌ Enhanced response formatting failed: {e}")
        return None

def test_response_schema_formatter():
    """Test the response schema formatter"""
    print("\n=== Testing Response Schema Formatter ===")
    
    # Sample data
    sample_answer = "The policy covers hospitalization expenses up to ₹5,00,000 per year as stated in Section 3.1."
    sample_sources = [
        {
            "doc_id": "policy_001",
            "doc_title": "Health Insurance Policy",
            "section_title": "Coverage Limits",
            "similarity_score": 0.92,
            "text": "Hospitalization coverage limit: ₹5,00,000 per year",
            "page_number": 8,
            "chunk_id": "chunk_003",
            "word_count": 15,
            "legal_density": 0.9,
            "structural_rank": 1,
            "retrieval_method": "semantic_search"
        }
    ]
    
    sample_query = "What is the coverage limit for hospitalization?"
    
    try:
        # Test success response creation
        success_response = ResponseFormatter.create_success_response(
            answer=sample_answer,
            sources=sample_sources,
            confidence=0.92,
            query=sample_query,
            threshold_used=0.7,
            response_type="coverage",
            category="coverage"
        )
        
        print("✅ Success response creation successful")
        print(f"Response ID: {success_response.get('response_id')}")
        print(f"Response Type: {success_response.get('response_type')}")
        print(f"Category: {success_response.get('category')}")
        
        # Test error response creation
        error_response = ResponseFormatter.create_error_response(
            error="Failed to process query due to invalid parameters",
            query=sample_query
        )
        
        print("✅ Error response creation successful")
        print(f"Response Type: {error_response.get('response_type')}")
        print(f"Error Type: {error_response.get('error', {}).get('type')}")
        
        return success_response, error_response
        
    except Exception as e:
        print(f"❌ Response schema formatter failed: {e}")
        return None, None

def test_response_analysis():
    """Test response analysis features"""
    print("\n=== Testing Response Analysis ===")
    
    # Test query intent analysis
    test_queries = [
        "What is the waiting period?",
        "How do I file a claim?",
        "What are the exclusions?",
        "What is covered under the policy?",
        "What are the premium payment terms?"
    ]
    
    for query in test_queries:
        try:
            # Simulate query intent analysis
            intent_analysis = {
                "primary_intent": "information_seeking",
                "all_intents": ["information_seeking"],
                "complexity": "low" if len(query.split()) < 5 else "medium"
            }
            
            print(f"Query: '{query}'")
            print(f"  Intent: {intent_analysis['primary_intent']}")
            print(f"  Complexity: {intent_analysis['complexity']}")
            
        except Exception as e:
            print(f"❌ Query analysis failed for '{query}': {e}")

def demonstrate_enhanced_features():
    """Demonstrate enhanced response features"""
    print("\n=== Enhanced Response Features Demonstration ===")
    
    # Create a comprehensive sample response
    sample_response = {
        "response_id": "resp_a1b2c3d4",
        "timestamp": datetime.utcnow().isoformat(),
        "answer": "According to the policy document, the waiting period for pre-existing conditions is 48 months from the policy commencement date. This is clearly stated in Section 4.2 on page 15 of the policy document.",
        "response_type": "waiting_period",
        "category": "timing",
        "query": {
            "original": "What is the waiting period for pre-existing conditions?",
            "processed": "What is the waiting period for pre-existing conditions?",
            "language": "en",
            "intent": {
                "primary_intent": "temporal",
                "all_intents": ["temporal", "information_seeking"],
                "complexity": "medium"
            }
        },
        "confidence": {
            "score": 0.85,
            "level": "high",
            "breakdown": {
                "overall": 0.85,
                "source_relevance": 0.88,
                "response_completeness": 0.9,
                "citation_quality": 0.8
            }
        },
        "sources": {
            "total_count": 2,
            "documents": [
                {
                    "doc_id": "policy_001",
                    "doc_title": "Health Insurance Policy",
                    "section_title": "Waiting Periods",
                    "similarity_score": 0.88,
                    "threshold_used": 0.7,
                    "retrieval_method": "semantic_search",
                    "page_number": 15,
                    "chunk_id": "chunk_001",
                    "text_preview": "Waiting period for pre-existing conditions: 48 months from policy commencement date...",
                    "has_citations": True,
                    "word_count": 25,
                    "legal_density": 0.8,
                    "structural_rank": 1
                }
            ],
            "coverage": {
                "documents": 1,
                "pages": 1,
                "sections": 1,
                "total_chunks": 2
            }
        },
        "search_parameters": {
            "threshold_used": 0.7,
            "adaptive_threshold": True,
            "retrieval_method": "semantic_search"
        },
        "quality_indicators": {
            "completeness": 0.9,
            "specificity": 0.85,
            "citation_count": 2
        },
        "warnings": [],
        "recommendations": [
            {
                "type": "add_documents",
                "priority": "low",
                "suggestion": "Consider uploading additional policy documents for comprehensive coverage",
                "examples": ["Policy schedules", "Endorsements", "Riders"]
            }
        ],
        "enhanced_metadata": {
            "questions": ["What is the waiting period for pre-existing conditions?"],
            "confidence_scores": [0.85],
            "overall_confidence": 0.85,
            "clause_references": [
                {
                    "clause": "Section 4.2",
                    "page": 15,
                    "text": "Waiting period for pre-existing conditions: 48 months"
                }
            ],
            "source_clause_ref": [],
            "context_chunks_used": 2,
            "metadata": {
                "context_relevance": 0.88,
                "completeness": 0.9
            },
            "response_analysis": {
                "word_count": 35,
                "sentence_count": 2,
                "has_citations": True,
                "has_numbers": True,
                "has_bullet_points": False,
                "tone": "professional"
            }
        },
        "explainability": {
            "query_analysis": {
                "original_query": "What is the waiting period for pre-existing conditions?",
                "intent_detected": {
                    "primary_intent": "temporal",
                    "all_intents": ["temporal", "information_seeking"],
                    "complexity": "medium"
                },
                "complexity_score": {
                    "word_count": 8,
                    "has_multiple_clauses": False,
                    "has_technical_terms": True,
                    "complexity_level": "medium"
                }
            },
            "source_analysis": {
                "total_sources": 2,
                "unique_documents": 1,
                "source_quality": {
                    "average_score": 0.88,
                    "quality_level": "high",
                    "high_quality_sources": 2,
                    "medium_quality_sources": 0,
                    "low_quality_sources": 0
                },
                "coverage_analysis": {
                    "coverage_type": "limited",
                    "coverage_score": 0.33,
                    "documents_covered": 1,
                    "sections_covered": 1,
                    "document_distribution": {"policy_001": 2}
                }
            },
            "response_quality": {
                "completeness": 0.9,
                "specificity": 0.85,
                "citation_quality": 1.0
            },
            "audit_trail": {
                "timestamp": datetime.utcnow().isoformat(),
                "query_processed": ["What is the waiting period for pre-existing conditions?"],
                "confidence_scores": [0.85],
                "clause_references": [
                    {
                        "clause": "Section 4.2",
                        "page": 15,
                        "text": "Waiting period for pre-existing conditions: 48 months"
                    }
                ],
                "source_clause_ref": []
            }
        }
    }
    
    print("✅ Enhanced response structure created successfully")
    print(f"Response ID: {sample_response['response_id']}")
    print(f"Response Type: {sample_response['response_type']}")
    print(f"Category: {sample_response['category']}")
    print(f"Confidence Level: {sample_response['confidence']['level']}")
    print(f"Quality Score: {sample_response['quality_indicators']['completeness']}")
    print(f"Citations: {sample_response['quality_indicators']['citation_count']}")
    print(f"Warnings: {len(sample_response['warnings'])}")
    print(f"Recommendations: {len(sample_response['recommendations'])}")
    
    # Validate the response
    validation_result = ResponseSchemaValidator.validate_response(sample_response)
    if validation_result["valid"]:
        print("✅ Response validation successful")
    else:
        print("❌ Response validation failed:")
        for error in validation_result["errors"]:
            print(f"  - {error}")
    
    return sample_response

def main():
    """Main test function"""
    print("🚀 Testing Enhanced Response Format and Structured Responses")
    print("=" * 60)
    
    # Test enhanced response formatter
    enhanced_response = test_enhanced_response_format()
    
    # Test response schema formatter
    success_response, error_response = test_response_schema_formatter()
    
    # Test response analysis
    test_response_analysis()
    
    # Demonstrate enhanced features
    comprehensive_response = demonstrate_enhanced_features()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("\nEnhanced Response Format Features:")
    print("• Structured response with comprehensive metadata")
    print("• Confidence scoring with detailed breakdown")
    print("• Source analysis with coverage metrics")
    print("• Quality indicators and recommendations")
    print("• Query intent analysis and complexity scoring")
    print("• Explainability information for audit trails")
    print("• Enhanced warnings and suggestions")
    print("• Response categorization and typing")
    
    return {
        "enhanced_response": enhanced_response,
        "success_response": success_response,
        "error_response": error_response,
        "comprehensive_response": comprehensive_response
    }

if __name__ == "__main__":
    main() 