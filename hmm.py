
#probs.py and sentiment.py are not included in this sample
import probs
import sentiment
import math

#An implementation of the Viterbi Algorithm

class HMM:
   
    #Get grades and sentences from movie reviews
    def __init__(self, p, testAuthChar):
        #self.p is the probs object which contains emission and transmission probabilities for this data 
        self.p = p
        if testAuthChar=='d':
            path='author1.txt'
            pPath = 'author1X.txt'
        else:
            path='author2.txt'
            pPath='author2X.txt'
        (self.grades, self.sentences, self.orderReviews) = sentiment.getSentences(path)
        self.paragraphs = sentiment.paragraphSentimentDict(pPath)

    #Runs viterbi on all of the reviews
    def predictAllReviews(self, useParaMarkers):
        predict= {}
        total = len(self.sentences)
        sum=0
        for review in self.sentences:
            print "Review " + str(sum) + " out of " + str(total)
            (prob, path) =self.viterbi(review,useParaMarkers)
            predict[review] = path
            sum+=1
        return predict
    
    '''The states -2 to 2 are used to label each sentence, where -2 is a very negative review,
       0 is a neutral review, and 2 is a very positive review. Taking the probabilities from 
       the probs object, performs the viterbi algorithm and gives labels [-2 to 2] with the max probability
       to unlabelled sentences '''
            
    def viterbi(self, review, useParaMarkers):
        states = ['-2', '-1', '0', '1', '2']
        V = []
        path = {}
        
        #used to denote the last sentence in a paragraph
        lastSent = []
        numSentences = 0
        
        #Gets the last sentence in a review. We use state "3" to denote the last sentence in a paragraph.
        for paragraph in self.sentences[review]:
            numSentences += len(self.sentences[review][paragraph])
            lastSent.append(numSentences - 1)
        
        sentNum = 0
        for y in states:
            path[y]=[]
        
        # if not useParaMarkers:
        #     V.append({})
        #     V[0]=1
        #     V[-1]=1
        #     V[0]=1
        #     V[1]=1
        #     V[2]=1
        
        # We use log probabilities to prevent underflow
                
        for para in self.sentences[review]:
            
            if useParaMarkers:
                emit_p = self.p.getEmissionProbDict(self.sentences[review][para][0])
                V.append({})
                newpath={}
                
                '''When transitioning from state y to 3, we get the 
                transition probability from going to state y to 
                the last sentence in a paragraph.
                Simularly, when transitioning from state 3 to y,
                we get the transition probability from going to state 3 to y. '''
                
                for y in states:
                    V[sentNum][y] = math.log(self.p.getTransitionProb(3, int(y))) + math.log( emit_p[int(y)])
                    newpath[y] = path[y] + [y]
                path=newpath
                sentNum+=1
            
                #the first sentence has already been computed so we will skip it
                first_sent = True
            
            for sent in self.sentences[review][para]:
                if useParaMarkers and first_sent:
                    first_sent = False
                    continue
                
                V.append({})
                newpath = {}
                if (sentNum in lastSent) and useParaMarkers:
                    for y in states:
                        emit_p = self.p.getEmissionProbDict(self.sentences[review][para][sent])
                        (prob, state) = max([( V[sentNum-1][y0] + math.log(self.p.getTransitionProb(int(y),3)) + math.log(emit_p[int(y)]), y0) for y0 in states])
                        V[sentNum][y] = prob
                        newpath[y] = path[state] + [y]
                    path = newpath
            
                else:
                    for y in states:
                        emit_p = self.p.getEmissionProbDict(self.sentences[review][para][sent])
                        if(sentNum==0):
                            (prob, state) = max([(math.log(1) + math.log(self.p.getTransitionProb(int(y0),(int(y)))) + math.log(emit_p[int(y)]), y0) for y0 in states])
                        else:
                            (prob, state) = max([(V[sentNum-1][y0] + math.log(self.p.getTransitionProb(int(y0),(int(y)))) + math.log(emit_p[int(y)]), y0) for y0 in states])
                        V[sentNum][y] = prob
                        newpath[y] = path[state] + [y]
                    path = newpath
            
                sentNum = sentNum + 1
        
        (prob, state) = max([(V[numSentences-1][y], y) for y in states])
        return (prob, path[state])

