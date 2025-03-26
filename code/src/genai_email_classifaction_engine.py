					 

import google.generativeai as genai
import os
import re
import email
import json
import io
import pdfminer.high_level
import docx
import logging
import uuid
from datetime import datetime, timedelta


# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Configure Gemini API
genai.configure(api_key="AIzaSyCXAifMXJsB7-2kwIYel72dWFdsSaJ2Awg")  # Replace with your key

TYPES = {
    "Adjustment": [""],
    "AU Transfer": [""],
    "Closing Notice": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal", "Ongoing Fee", "Letter of Credit Fee"],
    "Commitment Change": ["Cashless Roll", "Decrease", "Increase"],
    "Money Movement-Inbound": ["Principal", "Interest", "Principal + Interest", "Principal+Interest+Fee"],
    "Money Movement-Outbound": ["Timebound", "Foreign Currency"]
}

def extract_email_metadata(msg):
    """Extracts metadata from an email message."""
    logging.info("Extracting email metadata...")
    metadata = {
        "From": msg.get("From"),
        "To": msg.get("To"),
        "Cc": msg.get("Cc"),
        "Bcc": msg.get("Bcc"),
        "Subject": msg.get("Subject"),
        "Date": str(msg.get("Date")),
        "Message-ID": msg.get("Message-ID"),
        "In-Reply-To": msg.get("In-Reply-To"),
        "References": msg.get("References"),
        "Content-Type": msg.get("Content-Type"),
        "Content-Transfer-Encoding": msg.get("Content-Transfer-Encoding"),
        "Return-Path": msg.get("Return-Path"),
    }
    logging.info("Email metadata extracted successfully.")
    return metadata

def extract_signature(email_content):
    """Extracts signature from email content."""
    logging.info("Searching for email signature...")
    signature_patterns = [
        r"(Regards|Thanks|Best regards|Best|Sincerely|Thank you),?\s*(.*)",
        r"(Yours faithfully|Yours truly),?\s*(.*)",
    ]
    for pattern in signature_patterns:
        match = re.search(pattern, email_content, re.IGNORECASE | re.DOTALL)
        if match:
            logging.info(f"Signature extracted: {match.group(1)}")
            return {"Signature Type": match.group(1).strip(), "Signature Content": match.group(2).strip()}
	
    logging.warning("No signature detected.")
    return {"Signature Type": None, "Signature Content": None}

def extract_key_attributes(email_content):
    """Extracts key attributes from email content using Gemini API."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Extract key attributes from the following email content. Look for details such as dates, amounts, identifiers (e.g., CUSIP), bank names, terms, or other specific details relevant to financial transactions.

    Email Content:
    {email_content}

    Return the result in JSON format, where each key represents an attribute and each value represents the corresponding extracted value. If an attribute cannot be extracted, set its value to null.

    Example:
    {{
        "Loan Repayment Date": "10-Nov-2023",
        "Repayment Amount": "USD 10,000,000.00",
        "Deal CUSIP": "123456789",
        "Recipient Bank Name": "Wells Fargo National Association",
        "Term Option": "SOFR (UST)",
        "otherAttribute": "value",
        "missingAttribute": null
    }}
    """

    try:
        response = model.generate_content(prompt)
        result = response.text
        logging.debug(f"Gemini API raw response for attributes: {result}")

																			 
        cleaned_result = re.sub(r'^```json\s*|\s*```$', '', result, flags=re.MULTILINE).strip()
		
			
        return json.loads(cleaned_result)
								
										 
																  
					 

    except Exception as e:
        logging.error(f"Error during Gemini API attribute extraction: {e}")
        return {}

def classify_email_with_gemini(email_content, metadata, signature, attributes, types=TYPES):
    """Classifies an email and extracts attributes using Gemini API."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Classify the following email based on the request type and sub-request type, and include the provided attributes.

    Email Metadata:
    {json.dumps(metadata)}

    Email Signature:
    {json.dumps(signature)}

    Email Content:
    {email_content}

    Possible Request Types and Sub-Request Types:
    {json.dumps(types)}

    Pre-extracted Attributes:
    {json.dumps(attributes)}

    Return the result in JSON format:
    {{
        "Request Type": "<request type>",
        "Sub-Request Type": "<sub-request type>",
        "Confidence": <confidence score as a number between 0 and 1>,
        "Attributes": <pre-extracted attributes>
    }}

    If the email cannot be classified, return:
    {{"error": "Could not classify the email."}}
    """

    try:
        response = model.generate_content(prompt)
        result = response.text
        logging.debug(f"Gemini API raw response for classification: {result}")

																			 
        cleaned_result = re.sub(r'^```json\s*|\s*```$', '', result, flags=re.MULTILINE).strip()

			
        json_result = json.loads(cleaned_result)
        if "error" in json_result:
            return None, None, 0.0, {}
        return (
            json_result.get("Request Type"),
            json_result.get("Sub-Request Type"),
            json_result.get("Confidence"),
            json_result.get("Attributes", attributes)
			 
										 
																					 
																							 
        )
																						   

																				  
																  
																		  
															 
																			 
				 
												  

    except Exception as e:
        logging.error(f"Error during Gemini API classification: {e}")
        return None, None, 0.0, attributes

def extract_text_from_pdf(pdf_file_path):
    """Extracts text from a PDF file."""
    logging.info(f"Extracting text from PDF: {pdf_file_path}")
    try:
        text = pdfminer.high_level.extract_text(pdf_file_path)
        if text.strip():
            logging.info("Text successfully extracted from PDF.")
        else:
            logging.warning("Extracted text is empty. Check PDF format.")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(docx_file_path):
    """Extracts text from a Word document."""
    logging.info(f"Extracting text from DOCX: {docx_file_path}")
    try:
        doc = docx.Document(docx_file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        if text.strip():
            logging.info("Text successfully extracted from DOCX.")
        else:
            logging.warning("Extracted text is empty. Check DOCX content.")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        return ""

							

def process_email_file(file_path):
    """Processes an email file (.eml, .pdf, .docx) and extracts information."""
																 
    file_name, file_extension = os.path.splitext(file_path)
    logging.info(f"Processing file: {file_path}")

    if file_extension.lower() == '.eml':
        logging.info("Detected .eml format. Extracting email components...")
        try:
            with open(file_path, 'rb') as f:
                msg = email.message_from_binary_file(f)
            logging.info("Email file loaded successfully.")
            email_content = ""
            if msg.is_multipart():
								  
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        email_content += part.get_payload(decode=True).decode(errors='ignore')
                    elif content_type == 'application/pdf':
                        email_content += extract_text_from_pdf(io.BytesIO(part.get_payload(decode=True)))
                    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                        email_content += extract_text_from_docx(io.BytesIO(part.get_payload(decode=True)))
            else:
                email_content = msg.get_payload(decode=True).decode(errors='ignore')

            metadata = extract_email_metadata(msg)
            signature = extract_signature(email_content)
			
																		   
            attributes = extract_key_attributes(email_content)

            request_type, sub_request_type, confidence, attributes = classify_email_with_gemini(
                email_content, metadata, signature, attributes
            )
            return request_type, sub_request_type, confidence, metadata, signature, attributes, email_content

								 
											 
												  
        except Exception as e:
            logging.error(f"Error processing .eml file: {e}")
            return None, None, 0.0, None, None, {}, ""

    elif file_extension.lower() == '.pdf':
        logging.info("Detected .pdf format. Extracting text...")
        try:
            email_content = extract_text_from_pdf(file_path)
            metadata = {"Subject": "PDF Document", "From": "Unknown", "To": "Unknown", "Date": "Unknown"}
            signature = extract_signature(email_content)
			
																		 
            attributes = extract_key_attributes(email_content)

            request_type, sub_request_type, confidence, attributes = classify_email_with_gemini(
                email_content, metadata, signature, attributes
            )
            return request_type, sub_request_type, confidence, metadata, signature, attributes, email_content

        except Exception as e:
            logging.error(f"Error processing .pdf file: {e}")
            return None, None, 0.0, None, None, {}, ""

    elif file_extension.lower() == '.docx':
        logging.info("Detected .docx format. Extracting text...")
        try:
            email_content = extract_text_from_docx(file_path)
            metadata = {"Subject": "DOCX Document", "From": "Unknown", "To": "Unknown", "Date": "Unknown"}
            signature = extract_signature(email_content)
            attributes = extract_key_attributes(email_content)

            request_type, sub_request_type, confidence, attributes = classify_email_with_gemini(
                email_content, metadata, signature, attributes
            )
            return request_type, sub_request_type, confidence, metadata, signature, attributes, email_content

        except Exception as e:
            logging.error(f"Error processing .docx file: {e}")
            return None, None, 0.0, None, None, {}, ""

    else:
        logging.error("Unsupported file format!")
        return None, None, 0.0, None, None, {}, ""
 
								
															
													 
											 
						   

def create_service_intake_request(json_data, email_content):
    """Generates a service intake request using Gemini, including a description of the email intent."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert in generating service intake requests for a financial institution. Based on the provided email content and classified JSON data, create a service intake request with the following fields:
    - Request Type: From JSON "Request Type"
    - Sub-Request Type: From JSON "Sub-Request Type"
    - Assigned To: Assign a team or individual based on the request type and context (e.g., "Loan Processing Team" for loan-related requests, "General Support" for unknown types)
    - Summary: A concise summary of the request, capturing key details like amount, date, or identifiers (e.g., CUSIP)
    - Priority: "High", "Medium", or "Low" based on urgency (e.g., "High" for money movements or near deadlines, "Medium" for notices, "Low" for others)
    - Description: A brief narrative explaining the intent of the email (e.g., "Request to process a loan repayment")
    - Details: A dictionary with Sender, Recipient, Subject (from Metadata), and all Attributes

    Rules:
    - Use the email content to assess urgency, intent, and context (e.g., dates, phrases like "effective", "please confirm").
    - For the Description, focus on the purpose of the email (e.g., what action is being requested or notified).
    - If a date in Attributes (e.g., "Loan Repayment Date") is within 7 days from today ({datetime.now().strftime('%d-%b-%Y')}), set Priority to "High".
    - For "Money Movement-Inbound" or "Money Movement-Outbound", default to "High" priority unless overridden by lack of urgency.
    - Use these team assignments as a guide:
      - "Money Movement-Inbound": "Loan Processing Team"
      - "Money Movement-Outbound": "Outbound Team"
      - "Closing Notice": "Closing Team"
      - "Adjustment": "Adjustment Team"
      - "Commitment Change": "Commitment Team"
      - "AU Transfer": "Transfer Team"
      - Unknown: "General Support"

    Email Content:
    ```
    {email_content}
    ```
										  
									
						   
		 
									   
						

    Classified JSON Data:
    ```json
    {json.dumps(json_data, indent=4)}
    ```
										
																
										   
																 

    Return the result in JSON format:
    ```json
    {{
        "Request Type": "<request type>",
        "Sub-Request Type": "<sub-request type>",
        "Assigned To": "<team or individual>",
        "Summary": "<summary>",
        "Priority": "<High|Medium|Low>",
        "Description": "<intent of the email>",
        "Details": {{
            "Sender": "<sender>",
            "Recipient": "<recipient>",
            "Subject": "<subject>",
            "<attribute_key>": "<attribute_value>",
            ...
        }}
    }}
    ```

    Example:
    ```json
    {{
        "Request Type": "Money Movement-Inbound",
        "Sub-Request Type": "Principal",
        "Assigned To": "Loan Processing Team",
        "Summary": "Loan repayment of USD 10,000,000.00 for deal CUSIP 123456789 due 10-Nov-2023",
        "Priority": "High",
        "Description": "Request to process a loan repayment of USD 10,000,000.00 for John Cena L.P., effective 10-Nov-2023, with confirmation requested.",
        "Details": {{
            "Sender": "Bank of America <notifications@bofa.com>",
            "Recipient": "Wells Fargo National Association <transactions@wellsfargo.com>",
            "Subject": "Loan Repayment Notification - John Cena L.P.",
            "Loan Repayment Date": "10-Nov-2023",
            "Repayment Amount": "USD 10,000,000.00",
            "Deal CUSIP": "123456789"
        }}
    }}
    ```
    """
    try:
        response = model.generate_content(prompt)
        result = response.text
        logging.debug(f"Gemini API raw response for service request: {result}")
        cleaned_result = re.sub(r'^```json\s*|\s*```$', '', result, flags=re.MULTILINE).strip()
        service_request = json.loads(cleaned_result)
        logging.info("Service intake request generated successfully.")
        return service_request
    except Exception as e:
        logging.error(f"Error generating service intake request with Gemini: {e}")
        # Fallback to basic structure if Gemini fails
        request_type = json_data.get("Request Type", "Unknown")
        sub_request_type = json_data.get("Sub-Request Type", "Unknown")
        metadata = json_data.get("Metadata", {})
        attributes = json_data.get("Attributes", {})
        return {
            "Request Type": request_type,
            "Sub-Request Type": sub_request_type,
            "Assigned To": "General Support",
            "Summary": f"{request_type}: {sub_request_type}",
            "Priority": "Low",
            "Description": "Unable to determine email intent due to processing error.",
            "Details": {
                "Sender": metadata.get("From", "Unknown"),
                "Recipient": metadata.get("To", "Unknown"),
                "Subject": metadata.get("Subject", "Unknown"),
                **attributes
            }
        }

if __name__ == "__main__":
    file_path = input("Enter the path to your email file (.eml, .pdf, or .docx): ")
    logging.info("Running the email classifier pipeline...")
    
    request_type, sub_request_type, confidence, metadata, signature, attributes, email_content = process_email_file(file_path)
    
    if request_type and sub_request_type:
        output_json = {
            "Request Type": request_type,
            "Sub-Request Type": sub_request_type,
            "Confidence": confidence,
            "Metadata": metadata,
            "Signature": signature,
            "Attributes": attributes,
        }
        print("Classified Email JSON:")
        print(json.dumps(output_json, indent=4))
        
        service_request = create_service_intake_request(output_json, email_content)
        print("\nService Intake Request:")
        print(json.dumps(service_request, indent=4))
        
        # Save outputs
        with open("email_classification.json", "w") as f:
            json.dump(output_json, f, indent=4)
        with open("service_intake_request.json", "w") as f:
            json.dump(service_request, f, indent=4)
        logging.info("Outputs saved to email_classification.json and service_intake_request.json")
    else:
        print(json.dumps({"error": "Could not classify the email."}, indent=4))