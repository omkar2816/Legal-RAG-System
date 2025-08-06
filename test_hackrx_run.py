import requests
import os
import time

# Test script to verify that the /hackrx/run endpoint processes files synchronously

def test_hackrx_run():
    """Test the /hackrx/run endpoint to ensure files are processed before answering questions"""
    print("Testing /hackrx/run endpoint...")
    
    # URL for the API endpoint
    url = "http://localhost:8000/hackrx/run"
    
    # Sample PDF file to upload (replace with an actual file path)
    test_file_path = "./test_data/sample.pdf"
    
    # Check if the test file exists
    if not os.path.exists(test_file_path):
        print(f"Test file not found: {test_file_path}")
        print("Please create a test file or update the path in the script.")
        return
    
    # Sample questions to ask
    questions = "What is the main topic of this document?, What are the key points?"
    
    # Prepare the files and form data
    files = {
        'files': open(test_file_path, 'rb')
    }
    data = {
        'questions': questions
    }
    
    try:
        # Start timing
        start_time = time.time()
        
        # Make the request
        print("Sending request to /hackrx/run...")
        response = requests.post(url, files=files, data=data)
        
        # End timing
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check the response
        if response.status_code == 200:
            print(f"Request successful! Response received in {total_time:.2f} seconds")
            
            # Parse the response
            result = response.json()
            
            # Check if documents were processed
            if 'documents' in result:
                print(f"Documents processed: {len(result['documents'])}")
                for doc in result['documents']:
                    print(f"  - {doc['filename']}: {doc['processing_status']}")
                    if 'processing_time' in doc:
                        print(f"    Processing time: {doc['processing_time']}")
            
            # Check if answers were provided
            if 'answers' in result:
                print(f"\nAnswers provided: {len(result['answers'])}")
                for i, answer in enumerate(result['answers']):
                    print(f"\nQuestion {i+1}: {answer['question']}")
                    print(f"Answer: {answer['answer'][:100]}..." if len(answer['answer']) > 100 else f"Answer: {answer['answer']}")
                    if 'processing_time' in answer:
                        print(f"Processing time: {answer['processing_time']}")
            
            # Check total processing time
            if 'processing_time' in result:
                print(f"\nTotal processing time reported by API: {result['processing_time']}")
                
            print(f"\nActual request-response time: {total_time:.2f} seconds")
            
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
    
    except Exception as e:
        print(f"Error occurred: {e}")
    
    finally:
        # Close the file
        files['files'].close()

if __name__ == "__main__":
    test_hackrx_run()