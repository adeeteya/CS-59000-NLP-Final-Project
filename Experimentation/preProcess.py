import os
import re
import spacy
import spacy_transformers
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.downloader import download as nltk_download

# Load spaCy model
nlp = spacy.load("en_core_web_trf")  # Uses transformer-based model for legal language

# Download NLTK resources
nltk_download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def extract_legal_phrases(text):
    # Automatically extracts legal phrases from text using spaCy and TF-IDF.
    doc = nlp(text)
    
    # Step 1: Collect noun chunks and named entities as legal phrases
    legal_phrases = set()
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1:  # Keep multi-word expressions
            legal_phrases.add(chunk.text)
    for ent in doc.ents:
        if ent.label_ in ["LAW", "ORG", "MISC", "PRODUCT", "GPE", "DATE", "PERSON", "MONEY", "PERCENT", "NORP", "FAC"]: # Entities relevant to T&Cs
            legal_phrases.add(ent.text)

    return list(legal_phrases)

# Function to preprocess terms using the legal phrases
def preprocess_terms(text, legal_phrases):
    sentences = sent_tokenize(text.lower())  # Lowercase for uniform processing
    preprocessed_sentences = []

    for sentence in sentences:
        tokens = [lemmatizer.lemmatize(word) for word in re.findall(r'\b\w+\b', sentence)]
        
        # Filter tokens based on stop words and legal phrases
        processed_sentence = ' '.join([
            word if word in legal_phrases else word for word in tokens
        ])
        preprocessed_sentences.append(processed_sentence)

    # Join preprocessed sentences
    return '. '.join(preprocessed_sentences)

# Function to process all files in the "DataSet" folder
def preprocess_folder(folder_path="DataSet"):
    # Get the path where this script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Iterate through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Process only .txt files
            input_path = os.path.join(folder_path, filename)
            
            # Read input file
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Extract legal phrases from the document
            legal_phrases = extract_legal_phrases(text)

            # Preprocess using the extracted phrases
            processed_text = preprocess_terms(text, legal_phrases)

            # Write to the output file
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(processed_text)

            print(f"Processed file saved to {input_path}")

# Process all files in the DataSet folder
preprocess_folder()
