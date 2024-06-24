import re

# get the last word of a sentence
def get_last_word(sentence):
    # Strip leading/trailing whitespace
    sentence = sentence.strip()

    # Split the sentence into words using space as the delimiter
    words = sentence.split()

    # Get the last word in the list
    last_word = words[-1] if words else ''

    # Remove punctuation from the last word using a regular expression
    last_word = re.sub(r'[.,!?;:]', '', last_word)

    return last_word