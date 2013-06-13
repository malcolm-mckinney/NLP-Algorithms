import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer


# Runs Lesks Algorithm in order to compute the best sense of the word in a given context
# Takes in a single word as a string and a string of words as arguments
# Runs compute_overlap and returns the sense definition with the largest overlap

def lesk_algo(word, sentence): 
    context = wordpunct_tokenize(sentence)
    if word not in context:
        return word + " is not in the sentence!!"
    senses = get_senses(word)
    if not senses:
        return "There are no senses availible for the word: " + word + "\n"
    best_sense = senses[0]
    max_overlap = 0
    for sense in senses:
        overlap = compute_overlap(get_signature(sense), context)
        if overlap > max_overlap:
            max_overlap = overlap
            best_sense = sense
    return best_sense.definition


# Computes the overlap between the context and the dictionary entries for a word
# Returns the score for overlap

def compute_overlap(signature, context):
    overlap = 0
    definition, examples = signature
    #Imports the stopwords from stopword corpus
    stopwords = nltk.corpus.stopwords.words('english')
    #Makes an instance of the lemmatizer
    lmtzr = WordNetLemmatizer()
    def_arr = []
    ex_arr = []
    new_context = []
    for c in context:
        word = c.lower()
        if word not in stopwords:
            new_context.append(word)
    for c in new_context:
        word = lmtzr.lemmatize(c)
        overlap, def_arr = overlap_helper(word, definition, stopwords, lmtzr, def_arr, overlap)
        overlap, ex_arr = overlap_helper(word, examples, stopwords, lmtzr, ex_arr, overlap)
    print str(overlap)
    return overlap

# Uses wordnet to find all of the senses of a given word

def get_senses(word):
    senses = []
    for synset in wn.synsets(word):
        senses.append(synset)
    return senses

# For a given sense, retuns the dictionary defnition and the examples for that sense

def get_signature(sense):
    definition = ""
    print "Sense: " + sense.definition
    if sense.definition:
        definition = wordpunct_tokenize(sense.definition)   
    return (definition, examples)


# A helper for the compute overlap function.
# Takes in a term from the dictionary and the context.
# Takes in the stopwords, lemmatizer object and the old array
# Returns a number that is used for the overlap and the new array.
def overlap_helper(term, signature, stopwords, lem, old, old_overlap): 
    new = []
    index = 0
    overlap = old_overlap
    for s in signature:
        word = s.lower()
        if word not in stopwords:
            if term.lower() == lem.lemmatize(word).lower():
                found = False
                for (ind, succ) in old:
                    if ind == index:
                        found = True
                        tuple = (index +1, succ + 1)
                        new.append(tuple)
                        overlap = overlap + (2 ** succ)
                if not found:
                    tuple = (index + 1, 1)
                    new.append(tuple)
                    overlap = overlap + 1
        index = index + 1
    return (overlap, new) 


if __name__ == "__main__":
    # Returns the singing sence of the word. 
    print lesk_algo("bass", "The lowest adult male singing voice is the bass")      
