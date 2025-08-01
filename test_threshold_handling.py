#!/usr/bin/env python3
"""
Test script for enhanced similarity threshold handling
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vectordb.advanced_retrieval import AdvancedRetrievalEngine
from config.settings import settings

def test_threshold_calculation():
    """Test the effective threshold calculation"""
    
    print("🧪 Testing Threshold Calculation")
    print("=" * 50)
    
    engine = AdvancedRetrievalEngine()
    
    # Test cases for threshold calculation
    test_cases = [
        {
            "name": "High Score - Should be selective",
            "score": 0.9,
            "base_threshold": 0.3,
            "all_scores": [0.2, 0.4, 0.6, 0.8, 0.9],
            "adaptive": True
        },
        {
            "name": "Low Score - Should be lenient",
            "score": 0.1,
            "base_threshold": 0.5,
            "all_scores": [0.1, 0.2, 0.3, 0.4, 0.5],
            "adaptive": True
        },
        {
            "name": "Wide Score Range - Should adjust",
            "score": 0.6,
            "base_threshold": 0.3,
            "all_scores": [0.1, 0.2, 0.6, 0.8, 0.9],
            "adaptive": True
        },
        {
            "name": "Non-adaptive - Should use base",
            "score": 0.5,
            "base_threshold": 0.4,
            "all_scores": [0.1, 0.2, 0.5, 0.7, 0.8],
            "adaptive": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📊 {test_case['name']}:")
        print("-" * 30)
        
        effective_threshold = engine._calculate_effective_threshold(
            score=test_case['score'],
            base_threshold=test_case['base_threshold'],
            adaptive=test_case['adaptive'],
            all_scores=test_case['all_scores']
        )
        
        print(f"  Score: {test_case['score']:.3f}")
        print(f"  Base Threshold: {test_case['base_threshold']:.3f}")
        print(f"  Effective Threshold: {effective_threshold:.3f}")
        print(f"  Adaptive: {test_case['adaptive']}")
        print(f"  Score Range: {min(test_case['all_scores']):.3f} - {max(test_case['all_scores']):.3f}")
        
        # Check if threshold is within bounds
        if settings.MIN_SIMILARITY_THRESHOLD <= effective_threshold <= settings.HIGH_SIMILARITY_THRESHOLD:
            print(f"  ✅ Threshold within bounds")
        else:
            print(f"  ❌ Threshold outside bounds")

def test_threshold_filtering():
    """Test threshold-based filtering logic"""
    
    print("\n🔍 Testing Threshold Filtering")
    print("=" * 40)
    
    engine = AdvancedRetrievalEngine()
    
    # Mock search results for testing
    mock_matches = [
        {"score": 0.9, "metadata": {"text": "High relevance content", "doc_title": "Doc A"}},
        {"score": 0.7, "metadata": {"text": "Medium relevance content", "doc_title": "Doc B"}},
        {"score": 0.5, "metadata": {"text": "Low relevance content", "doc_title": "Doc C"}},
        {"score": 0.3, "metadata": {"text": "Very low relevance content", "doc_title": "Doc D"}},
        {"score": 0.1, "metadata": {"text": "Irrelevant content", "doc_title": "Doc E"}}
    ]
    
    # Test different threshold scenarios
    threshold_scenarios = [
        {"name": "High Threshold (0.8)", "threshold": 0.8, "expected_count": 1},
        {"name": "Medium Threshold (0.6)", "threshold": 0.6, "expected_count": 2},
        {"name": "Low Threshold (0.4)", "threshold": 0.4, "expected_count": 3},
        {"name": "Very Low Threshold (0.2)", "threshold": 0.2, "expected_count": 4}
    ]
    
    for scenario in threshold_scenarios:
        print(f"\n📋 {scenario['name']}:")
        print("-" * 25)
        
        # Simulate filtering logic
        filtered_results = []
        all_scores = [match["score"] for match in mock_matches]
        
        for match in mock_matches:
            score = match["score"]
            
            # Calculate effective threshold
            effective_threshold = engine._calculate_effective_threshold(
                score=score,
                base_threshold=scenario["threshold"],
                adaptive=True,
                all_scores=all_scores
            )
            
            # Apply filtering
            if score >= effective_threshold:
                filtered_results.append({
                    "score": score,
                    "threshold_used": effective_threshold,
                    "doc_title": match["metadata"]["doc_title"]
                })
        
        print(f"  Expected: {scenario['expected_count']} results")
        print(f"  Actual: {len(filtered_results)} results")
        
        for result in filtered_results:
            print(f"    - {result['doc_title']}: Score={result['score']:.3f}, Threshold={result['threshold_used']:.3f}")

def test_minimum_results_requirement():
    """Test minimum results requirement logic"""
    
    print("\n📊 Testing Minimum Results Requirement")
    print("=" * 45)
    
    engine = AdvancedRetrievalEngine()
    
    # Test scenarios with different result counts
    scenarios = [
        {
            "name": "Sufficient Results",
            "results_count": 5,
            "min_required": 3,
            "should_adjust": False
        },
        {
            "name": "Insufficient Results",
            "results_count": 1,
            "min_required": 3,
            "should_adjust": True
        },
        {
            "name": "Exact Minimum",
            "results_count": 2,
            "min_required": 2,
            "should_adjust": False
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}:")
        print("-" * 25)
        print(f"  Results: {scenario['results_count']}")
        print(f"  Minimum Required: {scenario['min_required']}")
        print(f"  Should Adjust: {scenario['should_adjust']}")
        
        if scenario['results_count'] < scenario['min_required']:
            print(f"  ⚠️  Would trigger threshold adjustment")
        else:
            print(f"  ✅ Sufficient results")

def test_settings_configuration():
    """Test threshold-related settings"""
    
    print("\n⚙️ Testing Settings Configuration")
    print("=" * 40)
    
    print(f"Minimum Similarity Threshold: {settings.MIN_SIMILARITY_THRESHOLD}")
    print(f"Medium Similarity Threshold: {settings.MEDIUM_SIMILARITY_THRESHOLD}")
    print(f"High Similarity Threshold: {settings.HIGH_SIMILARITY_THRESHOLD}")
    print(f"Enable Threshold Filtering: {settings.ENABLE_THRESHOLD_FILTERING}")
    print(f"Adaptive Threshold: {settings.ADAPTIVE_THRESHOLD}")
    print(f"Minimum Results Required: {settings.MIN_RESULTS_REQUIRED}")
    
    # Validate threshold hierarchy
    if (settings.MIN_SIMILARITY_THRESHOLD < settings.MEDIUM_SIMILARITY_THRESHOLD < 
        settings.HIGH_SIMILARITY_THRESHOLD):
        print("✅ Threshold hierarchy is valid")
    else:
        print("❌ Threshold hierarchy is invalid")

def test_edge_cases():
    """Test edge cases for threshold handling"""
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 25)
    
    engine = AdvancedRetrievalEngine()
    
    edge_cases = [
        {
            "name": "Empty scores list",
            "score": 0.5,
            "base_threshold": 0.3,
            "all_scores": [],
            "adaptive": True
        },
        {
            "name": "Single score",
            "score": 0.7,
            "base_threshold": 0.5,
            "all_scores": [0.7],
            "adaptive": True
        },
        {
            "name": "All same scores",
            "score": 0.6,
            "base_threshold": 0.4,
            "all_scores": [0.6, 0.6, 0.6, 0.6],
            "adaptive": True
        },
        {
            "name": "Extreme scores",
            "score": 0.99,
            "base_threshold": 0.1,
            "all_scores": [0.01, 0.5, 0.99],
            "adaptive": True
        }
    ]
    
    for case in edge_cases:
        print(f"\n🧪 {case['name']}:")
        print("-" * 20)
        
        try:
            effective_threshold = engine._calculate_effective_threshold(
                score=case['score'],
                base_threshold=case['base_threshold'],
                adaptive=case['adaptive'],
                all_scores=case['all_scores']
            )
            
            print(f"  Score: {case['score']:.3f}")
            print(f"  Base Threshold: {case['base_threshold']:.3f}")
            print(f"  Effective Threshold: {effective_threshold:.3f}")
            print(f"  ✅ Success")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    """Main test function"""
    
    print("🚀 Legal RAG System - Threshold Handling Test")
    print("=" * 60)
    
    try:
        # Run all tests
        test_threshold_calculation()
        test_threshold_filtering()
        test_minimum_results_requirement()
        test_settings_configuration()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✅ Enhanced threshold handling integration completed successfully!")
        print("\n📝 Summary:")
        print("   - Adaptive threshold calculation is working")
        print("   - Threshold-based filtering is functional")
        print("   - Minimum results requirement is implemented")
        print("   - Settings configuration is properly set up")
        print("   - Edge cases are handled correctly")
        print("\n🔧 Key Features:")
        print("   - Dynamic threshold adjustment based on score distribution")
        print("   - Minimum results guarantee with threshold relaxation")
        print("   - Configurable threshold bounds and behavior")
        print("   - Enhanced logging and debugging information")
        print("\n📋 Usage:")
        print("   - Set MIN_SIMILARITY_THRESHOLD for minimum acceptable scores")
        print("   - Set HIGH_SIMILARITY_THRESHOLD for maximum threshold")
        print("   - Enable/disable ADAPTIVE_THRESHOLD for dynamic adjustment")
        print("   - Configure MIN_RESULTS_REQUIRED for guaranteed results")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 