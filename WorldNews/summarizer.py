import nltk
import re
from nltk.stem import WordNetLemmatizer   
from nltk.corpus import stopwords
from collections import defaultdict
stop_words = set(stopwords.words('english'))  
lr = WordNetLemmatizer()

# Clean the text function that performs text pre-processing
def clean_text(text:str):
    # Remove any characters that are not letters, numbers, spaces, or punctuation
    text = re.sub("[^a-zA-Zα-ωΑ-Ω0-9-?!,. ]+",'', text)
    
    # Tokenize the words and lemmatize each word, while converting all words to lowercase
    ltext = [lr.lemmatize(word).lower() for word in nltk.word_tokenize(text) if len(word) > 1 and word not in stop_words]
    
    # Return the original text and the pre-processed text
    return text, ltext

# Main summarization function that runs text summarization
def run_summarization(text:str):
    # Clean the text
    text, ltext = clean_text(text)
    
    # Create a dictionary to store the frequency of each word
    word_dict = defaultdict(int)
    for word in ltext:
        word_dict[word] += 1
    
    # Tokenize the text into sentences
    sents = nltk.sent_tokenize(text)
    
    # Calculate the score for each sentence based on the frequency of its words
    sent_scores = [
        sum([word_dict[lr.lemmatize(word).lower()] for word in nltk.word_tokenize(sent) if len(word) > 1 and word not in stop_words]) / len([word for word in nltk.word_tokenize(sent) if len(word) > 1 and word not in stop_words]) 
        for sent in sents[1:-1]
    ]
    
    # Calculate the average score for all sentences
    avg_value = sum(sent_scores) / len(sent_scores)
    
    # Calculate the value used to determine the number of sentences to include in the summary
    value_c = 5 / len(sents)
    
    # Initialize the list to store the sentences in the summary
    sum_sents = [sents[0]]
    
    # Iterate over the scores of each sentence and add sentences with scores higher than the average score to the summary
    for i, score in enumerate(sent_scores):
        if score > avg_value and len(sum_sents) < int(len(sents) * value_c):
            sent = sents[i + 1]
            # Check if the sentence ends with a quote and add the sentence to the summary with proper punctuation
            if sent.count('"') / 2 != sent.count('"') // 2:
                sum_sents.append(str(sent[:-1] + '".').replace('""', '"'))
            else:
                sum_sents.append(sent)
    
    # Join the sentences in the summary
    
    sum_text = ' '.join(sum_sents)
    
    print("Now summarized and reduced by ", 1-len(nltk.word_tokenize(sum_text))/len(nltk.word_tokenize(text)), "====================== From ", len(nltk.word_tokenize(text)), " to ", len(nltk.word_tokenize(sum_text)))
    
    return sum_text;


