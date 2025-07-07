"""
Preprocesamiento de texto para análisis de letras
Adaptado para funcionar independientemente del proyecto ml-project-models
"""

import re
import string
from collections import Counter
from typing import List, Tuple, Dict, Optional
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import warnings
warnings.filterwarnings('ignore')

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class TextPreprocessor:
    """
    Text preprocessing class for lyrics data
    """

    def __init__(self, language: str = 'english'):
        """
        Initialize the preprocessor

        Args:
            language: Language for stopwords (default: english)
        """
        self.language = language
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words(language))

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Input text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Remove social media mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove punctuation except apostrophes (for contractions)
        text = re.sub(r'[^a-zA-Z\s\']', ' ', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Tokenize
        tokens = word_tokenize(text)

        # Remove stopwords and very short words
        tokens = [token for token in tokens
                 if token not in self.stop_words
                 and len(token) > 1]

        # Stem words
        tokens = [self.stemmer.stem(token) for token in tokens]

        # Join back to string
        return ' '.join(tokens)

    def extract_features(self, text: str) -> Dict[str, any]:
        """
        Extract various features from text

        Args:
            text: Input text

        Returns:
            Dictionary with extracted features
        """
        if not text:
            return {}

        # Basic text statistics
        words = text.split()
        characters = list(text)

        features = {
            'word_count': len(words),
            'char_count': len(characters),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'sentence_count': text.count('.') + text.count('!') + text.count('?'),
            'uppercase_ratio': sum(1 for c in characters if c.isupper()) / len(characters) if characters else 0,
            'punctuation_ratio': sum(1 for c in characters if c in string.punctuation) / len(characters) if characters else 0,
        }

        # Lexical diversity
        unique_words = set(words)
        features['lexical_diversity'] = len(unique_words) / len(words) if words else 0

        # Common word patterns
        features['repeated_chars'] = len(re.findall(r'(.)\1{2,}', text))
        features['all_caps_words'] = sum(1 for word in words if word.isupper() and len(word) > 1)

        return features

    def get_word_frequencies(self, texts: List[str], top_n: int = 100) -> Dict[str, int]:
        """
        Get word frequencies across multiple texts

        Args:
            texts: List of texts to analyze
            top_n: Number of top words to return

        Returns:
            Dictionary with word frequencies
        """
        all_words = []
        for text in texts:
            cleaned = self.clean_text(text)
            all_words.extend(cleaned.split())

        word_freq = Counter(all_words)
        return dict(word_freq.most_common(top_n))

    def remove_duplicates(self, texts: List[str], threshold: float = 0.8) -> List[str]:
        """
        Remove near-duplicate texts based on similarity threshold

        Args:
            texts: List of texts to deduplicate
            threshold: Similarity threshold (0-1)

        Returns:
            List of unique texts
        """
        unique_texts = []

        for text in texts:
            is_duplicate = False
            text_words = set(self.clean_text(text).split())

            for unique_text in unique_texts:
                unique_words = set(self.clean_text(unique_text).split())

                if not text_words or not unique_words:
                    continue

                # Calculate Jaccard similarity
                intersection = len(text_words.intersection(unique_words))
                union = len(text_words.union(unique_words))
                similarity = intersection / union if union > 0 else 0

                if similarity >= threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_texts.append(text)

        return unique_texts

    def clean_dataset(self, texts: List[str], min_words: int = 5,
                     max_words: int = 1000, remove_dups: bool = True) -> List[str]:
        """
        Clean entire dataset

        Args:
            texts: List of texts to clean
            min_words: Minimum word count
            max_words: Maximum word count
            remove_dups: Whether to remove duplicates

        Returns:
            List of cleaned texts
        """
        cleaned_texts = []

        for text in texts:
            if not text or not isinstance(text, str):
                continue

            cleaned = self.clean_text(text)
            word_count = len(cleaned.split())

            # Filter by word count
            if min_words <= word_count <= max_words:
                cleaned_texts.append(text)  # Keep original text, not cleaned version

        # Remove duplicates if requested
        if remove_dups:
            cleaned_texts = self.remove_duplicates(cleaned_texts)

        return cleaned_texts

def preprocess_lyrics_dataset(df, text_column: str = 'lyrics',
                            label_column: str = 'explicit',
                            preprocessor: Optional[TextPreprocessor] = None) -> Tuple[List[str], List[int]]:
    """
    Preprocess a lyrics dataset for training

    Args:
        df: DataFrame with lyrics data
        text_column: Name of the text column
        label_column: Name of the label column
        preprocessor: TextPreprocessor instance (creates new if None)

    Returns:
        Tuple of (texts, labels)
    """
    if preprocessor is None:
        preprocessor = TextPreprocessor()

    # Filter out missing values
    df = df.dropna(subset=[text_column, label_column])

    # Clean texts
    texts = df[text_column].tolist()
    texts = preprocessor.clean_dataset(texts)

    # Get corresponding labels
    labels = []
    original_texts = df[text_column].tolist()

    for text in texts:
        try:
            idx = original_texts.index(text)
            labels.append(df.iloc[idx][label_column])
        except ValueError:
            continue

    return texts, labels
