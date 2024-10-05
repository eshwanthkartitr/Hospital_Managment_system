import spacy
import PyPDF2
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load the English language model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def preprocess_text(text):
    doc = nlp(text.lower())
    return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.has_vector]

def get_document_embedding(text):
    doc = nlp(" ".join(preprocess_text(text)))
    return doc.vector

def calculate_similarity(vec1, vec2):
    return cosine_similarity(vec1.reshape(1, -1), vec2.reshape(1, -1))[0][0]

def review_resume(resume_path, job_description):
    # Extract text from resume
    resume_text = extract_text_from_pdf(resume_path)

    # Preprocess texts
    resume_processed = preprocess_text(resume_text)
    job_processed = preprocess_text(job_description)

    # Get document embeddings
    resume_embedding = get_document_embedding(resume_text)
    job_embedding = get_document_embedding(job_description)

    # Calculate similarity
    similarity_score = calculate_similarity(resume_embedding, job_embedding)

    print(f"\nResume Match Score: {similarity_score * 100:.2f}%")

    # Find most relevant words
    resume_words = set(resume_processed)
    job_words = set(job_processed)
    common_words = resume_words.intersection(job_words)

    # Calculate word importance
    word_importance = {}
    for word in common_words:
        word_vec = nlp(word).vector
        importance = calculate_similarity(word_vec, job_embedding)
        word_importance[word] = importance

    # Print top relevant words
    top_words = sorted(word_importance.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nTop relevant words in the resume:")
    for word, importance in top_words:
        print(f"{word}: {importance:.4f}")

    # Suggest improvements
    missing_words = job_words - resume_words
    if missing_words:
        print("\nRelevant words missing from the resume:")
        for word in list(missing_words)[:5]:
            print(word)

    return similarity_score

def hr_review():
    resume_path = input("Enter the path to the employee's resume PDF: ")
    job_description = input("Enter the job description: ")

    similarity_score = review_resume(resume_path, job_description)

    while True:
        decision = input("\nBased on this analysis, do you want to hire the candidate? (yes/no): ").lower()
        if decision in ['yes', 'no']:
            break
        print("Please enter 'yes' or 'no'.")

    if decision == 'yes':
        print("Great! The candidate has been approved for hiring.")
    else:
        print("The candidate has not been approved for hiring.")

    additional_notes = input("Enter any additional notes about this candidate: ")
    print("\nThank you for your review. Your decision and notes have been recorded.")

    # Here you could add code to save the decision and notes to a database or file

if __name__ == "__main__":
    print("Welcome to the Admin Resume Review System")
    hr_review()
