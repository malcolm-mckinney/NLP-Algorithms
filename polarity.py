'''The file parser class is not availible in this GitHub repository
   It takes a file of both labled and unlabeled hotel reviews
   and puts them into dictionaries for easy access '''

import FileParser, nltk, pickle, re, math

#An implementation of Naive Bayes Algorithm
class Polarity:

    def __init__(self):
        
        # this tag list was used to check if Naive bayes would work better on part of speech tagged sentences
        # we descovered that it actually performed worse with tagged sentences.
    
        
        self.tag_list = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'VBN']
        
        a, polarities, reviews = FileParser.parseTrain()
        
        self.bayes = self.seperate_reviews(polarities, reviews)
        
    # Takes all of the labeled reviews and tags the word depending on whether it was in a positive review or negtive one
    # Returns a bayes object that contains the lists of positive and negative lists
    
    def seperate_reviews(self, polarity_list, review_list):
        negative_words = []
        positive_words = []
        num_pos = 0
        num_neg = 0
        tokenizer = nltk.RegexpTokenizer('\w+')
        for p in range(len(polarity_list)):
            slist = self.splitParagraphIntoSentences(review_list[p])
            list = []
            if polarity_list[p] == '0':
                #words = tokenizer.tokenize(review_list[p])
                num_neg = num_neg + 1
                for s in slist:
                    words = tokenizer.tokenize(s)
                    try:
                        #tagged_words = nltk.pos_tag(words)
                        for word in words:
                            #if tag in self.tag_list and len(word) > 2:
                            word = word.lower()
                            o = ord(word[0])
                            if o >= ord('a') and o <= ord('z'):
                                list.append(word)
                    except:
                        pass
            
                if len(list) > 0:
                    negative_words.append((list, 'negative'))
                    
            else:
                num_pos = num_pos + 1
                for s in slist:
                    words = tokenizer.tokenize(s)
                    try:
                        #tagged_words = nltk.pos_tag(words)
                        for word in words:
                            #if tag in self.tag_list:
                            word = word.lower()
                            o = ord(word[0])
                            if o >= ord('a') and o <= ord('z'):
                                list.append(word.lower())
                    except:
                        pass
                                          
                if len(list) > 0:
                    positive_words.append((list,'positive'))
    
        all_words = positive_words + negative_words
        
        bayes = Bayes(num_pos, num_neg)
        bayes.add(all_words)
        return bayes

    def splitParagraphIntoSentences(self, paragraph):
    
    #   regular expressions are easiest (and fastest)
        sentenceEnders = re.compile('[.!?]')
        sentenceList = sentenceEnders.split(paragraph)
        return sentenceList   
    
    # Determines false negative/ false positive rate used to check the accuracy of our bayes model
    # In our report, we achieved a 95% correctness on guessing the polarity of an online review  
    
    def validate(self):
        a, polarities, reviews = FileParser.parseValidate()
        num_reviews = len(reviews)
        tokenizer = nltk.RegexpTokenizer('\w+')
        num_pos_correct = 0.
        num_pos_incorrect = 0.
        num_neg_correct = 0.
        num_neg_incorrect = 0.
        pos_percentage = 0.
        neg_percenage = 0.
        miss_percentage = 0.
        self.bayes.train()
        output = ""
        
        
        for i in range(len(reviews)):
            slist = self.splitParagraphIntoSentences(reviews[i])

            list = []
            words = []
            for s in slist:
                try:
                    words = tokenizer.tokenize(s)
                    #tagged_words = nltk.pos_tag(words)
                    for word in words:
                        #if tag in self.tag_list:
                        word = word.lower()
                        o = ord(word[0])
                        if o >= ord('a') and o <= ord('z'):
                            list.append(word.lower())
                except:
                    pass
                words += list
            
            string = self.bayes.classify(words)
            if string[0] == 'p':
                output += "1" + "\n"
                if polarities[i] == '1':
                    num_pos_correct = num_pos_correct + 1
                else:
                    num_pos_incorrect = num_pos_incorrect + 1
            else:
                output += "0" + "\n"
                if polarities[i] == '0':
                    num_neg_correct = num_neg_correct + 1
                else:
                    num_neg_incorrect = num_neg_incorrect + 1
               
                       
        pos_count = num_pos_correct + num_neg_incorrect
        neg_count = num_neg_correct + num_pos_incorrect

        if pos_count > 0:
            pos_percentage = (num_pos_correct/pos_count) * 100
        if neg_count > 0:
            neg_percenage = (num_neg_correct/neg_count) * 100
        
        miss_percentage = ((num_neg_incorrect + num_pos_incorrect) / num_reviews) * 100

        print "Positive Guessed Correctly: " + str(pos_percentage) + "%"
        print "Negative Guessed Correctly: " + str(neg_percenage) + "%"
        print "Percent Guessed Incorrectly: " + str(miss_percentage) + "%"
        
        
    # Assigns 1 (positive) or 0 (negative) polarities to the unlabeled reviews. 

    def test(self):
        a, polarities, reviews = FileParser.parseTest()
        num_reviews = len(reviews)
        polarities = []
        tokenizer = nltk.RegexpTokenizer('\w+')
        self.bayes.train()
        print "Start Testing: \n"
        output = ""
        
        for i in range(len(reviews)):
            slist = self.splitParagraphIntoSentences(reviews[i])
            list = []
            for s in slist:
                words = tokenizer.tokenize(s)
                try:
                    #tagged_words = nltk.pos_tag(words)
                    for word in words:
                        #if tag in self.tag_list:
                        word = word.lower()
                        o = ord(word[0])
                        if o >= ord('a') and o <= ord('z'):
                            list.append(word.lower())
                except:
                    pass
            
            string = self.bayes.classify(list)
            if string == 'positive':
                polarities.append('1')
                output += "1" + "\n"
               
            else:
                polarities.append('0')
                output += "0" + "\n"
        print output
        return polarities


#A naive bayes implementation. 
class Bayes:

    def __init__(self, num_pos_reviews, num_neg_reviews):
        self.pos_dict_count = {}
        self.neg_dict_count = {}
        self.pos_dict_prob = {}
        self.neg_dict_prob = {}
        self.num_pos_reviews= num_pos_reviews
        self.num_neg_reviews = num_neg_reviews
        self.num_pos = 0
        self.num_neg = 0
        self.num_reviews = self.num_pos_reviews + self.num_neg_reviews

    def add(self, words):
        
        for (list, tag) in words:
            if tag == 'positive':
                for word in list:
                    if word in self.pos_dict_count:
                        self.pos_dict_count[word] = self.pos_dict_count[word] + 1
                        self.num_pos = self.num_pos + 1
                    else:
                        self.pos_dict_count[word] = 1
                        self.num_pos = self.num_pos + 1

            else:
                for word in list:
                    if word in self.neg_dict_count:
                        self.neg_dict_count[word] = self.neg_dict_count[word] + 1
                        self.num_neg = self.num_neg + 1
                    else:
                        self.neg_dict_count[word] = 1
                        self.num_neg = self.num_neg + 1
                        
    def train(self):
        for word in self.pos_dict_count:
            self.pos_dict_prob[word] = (1 + (self.pos_dict_count[word])) /float(self.num_pos)
        for word in self.neg_dict_count:
            self.neg_dict_prob[word] = (1 + (self.neg_dict_count[word])) / float(self.num_neg)

   #gives a polarity to a set of words using log probabilties
    def classify(self, words):
        neg_score = math.log(self.num_neg_reviews/float(self.num_reviews))
        pos_score = math.log(self.num_pos_reviews/float(self.num_reviews))
        for w in words:
            if w in self.pos_dict_prob:
                pos_score += math.log(self.pos_dict_prob[w])
            else:
                pos_score += math.log(1.0/(self.num_pos))
            if w in self.neg_dict_prob:
                neg_score += math.log(self.neg_dict_prob[w])
            else:
                neg_score += math.log(1.0/(self.num_neg))
        if pos_score > neg_score:
            return 'positive'
        return 'negative'

    





