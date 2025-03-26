# backend.py

import os
from typing import Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
from genai_email_classifaction_engine import process_email_file, create_service_intake_request

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/upload-email/', methods=['POST'])
def upload_email():
    """Handles email file uploads, processes them, and returns the service intake request."""
    try:
        if 'file' not in request.files:
            raise Exception("No file part in the request")
        file = request.files['file']
        if file.filename == '':
            raise Exception("No file selected for uploading")

        # Save the uploaded file
        file_path = f"temp_{file.filename}"
        file.save(file_path)

        # Process the email file
        request_type, sub_request_type, confidence, metadata, signature, attributes, email_content = process_email_file(file_path)

        # Construct the output dictionary
        output_json = {
            "Request Type": request_type,
            "Sub-Request Type": sub_request_type,
            "Confidence": confidence,
            "Metadata": metadata,
            "Signature": signature,
            "Attributes": attributes,
        }

        # Generate service intake request
        if request_type and sub_request_type:
            service_request = create_service_intake_request(output_json, email_content)
            result = {
                "filename": file.filename,
                "classification": output_json,
                "service_intake_request": service_request
            }
            return jsonify(result)
        else:
            raise Exception("Email processing failed.")

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True, port=8000)