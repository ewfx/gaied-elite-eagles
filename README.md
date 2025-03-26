# 🚀 Project Name

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---
# AI-Powered Email Processing System

## 🎯 Introduction
Introduction

This document provides a comprehensive guide for developers seeking to understand, utilize, and extend the AI-powered email processing system. The system is designed to extract key information from emails in various formats (.eml, .pdf, .docx) and classify them based on their content.

## 🎥 Demo
🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](#) (if applicable)  
🖼️ Screenshots:

![Screenshot 1](link-to-image)

## 💡 Inspiration
What inspired you to create this project? Describe the problem you're solving.

## ⚙️ What It Does
Solution: 
The system follows a modular AI pipeline architecture:

Ingestion Collection Stage : Gathers email data from different sources.
Preprocessing: processs the emails in various formats (.eml, .pdf, .docx) and extracts the email text
Metadata Extraction: Extracts email headers (sender, recipient, etc.).   
Email Signature Detection: Identifies and extracts email signatures.  
Confidence Score
Key Attributes Extraction: Uses the Gemini API to extract specific data from the email body (dates, amounts, etc.).   
Content Classification: Employs the Gemini API to classify emails into request types and sub request types.  

## 🛠️ How We Built It
## Dependencies
* Python 3.12.6
* pip (Package Installer for Python)
* A virtual environment (recommended)

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/ewfx/gaied-elite-eagles
    cd Email_Classification_Project
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    C:\Syed\Workspace\Hackathon_2025\Email_Classification_Project>python --version
    Python 3.12.6

    C:\Syed\Workspace\Hackathon_2025\Email_Classification_Project>pip --version
    pip 24.2 from C:\Syed\Workspace\Hackathon_2025\python-3.12.6\Lib\site-packages\pip (python 3.12)

    C:\Syed\Workspace\Hackathon_2025\Email_Classification_Project>python -m venv my_env

    C:\Syed\Workspace\Hackathon_2025\Email_Classification_Project>my_env\Scripts\activate

    (my_env) C:\Syed\Workspace\Hackathon_2025\Email_Classification_Project>
    ```

3.  **Install dependencies:**

    ```bash
    pip install google-generativeai
    pip install requests
    pip install pandas
    pip install matplotlib
    pip install requests
    pip install transformers
    pip install torch PyPDF2 pytesseract pdf2image
    pip install openai
    pip install spacy

    ```
  
4.  **Install Tesseract OCR (for PDF text extraction):**

    * You'll need to install Tesseract OCR separately.
    * **Windows:** Download the installer from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki) and add the Tesseract executable to your system's PATH environment variable.
   
5.  **Configure API Keys:**

    * Obtain the necessary API keys from Google Generative AI,and add the API key to the `genai_email_classifaction_engine.py` file

6.  **Run the application:**

    ```bash
    python src/main/genai_email_classifaction_engine.py #or however you start your program.
    ```
## Output

The system outputs extracted data and classification results in JSON format.

## File Details

* `genai_email_classifaction_engine.py`: Contains the main email processing logic.

## 🚧 Challenges We Faced
Describe the major technical or non-technical challenges your team encountered.

## 🏗️ Tech Stack
- 🔹 Frontend: React/TailwindCSS
- 🔹 Backend: Node.js / FastAPI / Django
- 🔹 Database: MongoDB
- 🔹 Other: Google Gemini/Open AI

## 👥 Team
- **Syed Ahmed Ali**
- **Konabhai Veera**
- **Samaddar Satyendra**
- **Bekkam Nagaraju**
- **Challa BalaKishore**
