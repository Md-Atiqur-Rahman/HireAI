import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Make sure stopwords are downloaded
nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())

    # Remove punctuation and stopwords
    keywords = [
        word for word in tokens
        if word.isalpha() and word not in stopwords.words('english')
    ]

    return set(keywords)
