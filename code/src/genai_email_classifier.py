# email_classifier.py

import google.generativeai as genai
import os
import re
import email
import json

# Configure your API key
genai.configure(api_key="AIzaSyCXAifMXJsB7-2kwIYel72dWFdsSaJ2Awg") 

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
    return metadata

def extract_signature(email_content):
    """Extracts signature from email content."""
    signature_patterns = [
        r"(Regards|Thanks|Best regards|Best|Sincerely|Thank you),?\s*(.*)",
        r"(Yours faithfully|Yours truly),?\s*(.*)",
    ]
    for pattern in signature_patterns:
        match = re.search(pattern, email_content, re.IGNORECASE | re.DOTALL)
        if match:
            return {"Signature Type": match.group(1).strip(), "Signature Content": match.group(2).strip()}
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
        print(f"DEBUG: Gemini API raw response for attributes: {result}")

        # Clean the response by removing ```json markers and extra whitespace
        cleaned_result = re.sub(r'^```json\s*|\s*```$', '', result, flags=re.MULTILINE).strip()
        
        try:
            parsed_result = json.loads(cleaned_result)
            return parsed_result
        except json.JSONDecodeError as e:
            print(f"DEBUG: Failed to parse cleaned Gemini API response as JSON: {e}")
            return {}

    except Exception as e:
        print(f"Error during Gemini API attribute extraction: {e}")
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
        print(f"DEBUG: Gemini API raw response for classification: {result}")

        # Clean the response by removing ```json markers and extra whitespace
        cleaned_result = re.sub(r'^```json\s*|\s*```$', '', result, flags=re.MULTILINE).strip()

        try:
            json_result = json.loads(cleaned_result)
            if "error" in json_result:
                return None, None, 0.0, {}
            return (
                json_result.get("Request Type"),
                json_result.get("Sub-Request Type"),
                json_result.get("Confidence"),
                json_result.get("Attributes", attributes)  # Fallback to pre-extracted if missing
            )
        except json.JSONDecodeError as e:
            print(f"DEBUG: Failed to parse cleaned Gemini API response as JSON: {e}")
            request_type_match = re.search(r'"Request Type"\s*:\s*"([^"]+)"', cleaned_result)
            sub_request_type_match = re.search(r'"Sub-Request Type"\s*:\s*"([^"]+)"', cleaned_result)
            confidence_match = re.search(r'"Confidence"\s*:\s*(\d+\.?\d*)', cleaned_result)

            if request_type_match and sub_request_type_match and confidence_match:
                request_type = request_type_match.group(1).strip()
                sub_request_type = sub_request_type_match.group(1).strip()
                confidence = float(confidence_match.group(1))
                return request_type, sub_request_type, confidence, attributes
            else:
                return None, None, 0.0, attributes

    except Exception as e:
        print(f"Error during Gemini API classification: {e}")
        return None, None, 0.0, attributes

def classify_eml_email(eml_file_path, types=TYPES):
    """Classifies an .eml file and returns classification, confidence, metadata, signature, and attributes."""
    try:
        with open(eml_file_path, 'rb') as f:
            msg = email.message_from_binary_file(f)

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    email_content = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            email_content = msg.get_payload(decode=True).decode(errors='ignore')

        metadata = extract_email_metadata(msg)
        signature = extract_signature(email_content)
        attributes = extract_key_attributes(email_content)

        request_type, sub_request_type, confidence, attributes = classify_email_with_gemini(
            email_content, metadata, signature, attributes
        )
        return request_type, sub_request_type, confidence, metadata, signature, attributes

    except FileNotFoundError:
        return None, None, 0.0, None, None, {}
    except Exception as e:
        print(f"Error processing .eml file: {e}")
        return None, None, 0.0, None, None, {}

if __name__ == "__main__":
    eml_file_path = input("Enter the path to your .eml file: ")

    request_type, sub_request_type, confidence, metadata, signature, attributes = classify_eml_email(eml_file_path)

    if request_type and sub_request_type:
        output_json = {
            "Request Type": request_type,
            "Sub-Request Type": sub_request_type,
            "Confidence": confidence,
            "Metadata": metadata,
            "Signature": signature,
            "Attributes": attributes,
        }
        print(json.dumps(output_json, indent=4))
    else:
        print(json.dumps({"error": "Could not classify the email."}, indent=4))