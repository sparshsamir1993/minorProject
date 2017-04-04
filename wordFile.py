from bs4 import BeautifulSoup
import requests
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from string import punctuation
import unicodedata
from heapq import nlargest
from collections import defaultdict

def getwashingtonPostCorpus(url, token):
    try:
        page = requests.get(url).content
    except:
        return(None, None)
    soup = BeautifulSoup(page, 'html.parser')

    if soup is None:
        return(None, None)
    text = "hello"
    if soup.find_all(token) is not None:
        text = ' '.join(map(lambda p: p.text, soup.find_all(token)))
    string_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    file_text = readFile("corpus.txt")
    if string_text in file_text:
        print "Already in corpus."
    else:
        writeInFile(string_text)
        return text, soup.title.text

def writeInFile(text, file):
    f = open("corpus.txt", "a+")
    for i in text:
        f.write(i)
    f.write("\n\n")

def readFile(file):
    try:
        f = open(file, "r")
        text = f.read()
        return text
    except:
        writeInFile("", file)

def readUrlCorpus():
    try:
        f = open("linkCorpus.txt", "r")
        text = f.read()
        return text
    except:
        writeInLinkCorpus("")

def writeInLinkCorpus(url):
    f = open("linkCorpus.txt", "a+")
    for i in url:
        f.write(i)
    f.write("\n")

def writeIntechSummaryCorpus(text):
    f = open("techSummaryCorpus.txt", "a+")
    for i in text:
        f.write(i + "  ")
    f.write("\n\n")

def scrapeSource(url, magicFrag='2017', scrapperFunction=getwashingtonPostCorpus, token='article'):
    urlBodies = {}
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'html.parser')
    numErr = 0
    urlCorpus = readUrlCorpus()
    for a in soup.findAll('a'):
        try:
            url = a['href']
            if ((url not in urlBodies) and (magicFrag is not None and magicFrag in url) or magicFrag is None):
                if url not in urlCorpus:
                    writeInLinkCorpus(url)
                    body = scrapperFunction(url, token)
                else:
                    print ("in urlCorpus")
                if (body and len(body) > 0):
                    urlBodies[url] = body
                print (url)
            else:
                print ("something")
        except:
            numErr =+ 1
    return urlBodies

class FrequencySummarizer:
    def __init__(self, min_cut=0.1, max_cut=0.9):
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stopwords = set(stopwords.words('english') +
                                list(punctuation) +
                                [u" 's",'"'])

    def _compute_frequencies(self, word_sent):
        freq = defaultdict(int)
        print word_sent
        for sentence in word_sent:
            for word in sentence:
                if word not in self._stopwords:
                    freq[word] += 1
        print freq
        try:
            m = float(max(freq.values()))
        except:
            m = 1
        print (m)
        for word in list(freq.keys()) :
            freq[word] = freq[word]/m
            if freq[word] > self._max_cut or freq[word] < self._min_cut:
                del freq[word]
        return freq
    def extractFeatures(self, article, n, customStopWords=None):
        text = article
        # title = article[1]
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        self._freq = self._compute_frequencies(word_sent)
        if n < 0:
            return nlargest(len(self.freq_keys()), self._freq, key=self._freq.get)
        else:
            return nlargest(n, self._freq, key=self._freq.get)
    def extractRawFrequencies(self, article):
        text = article
        # title = article[1]
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lowr()) for s in sentences]
        freq = defaultdict(int)
        for s in word_sent:
            for word in s :
                if word not in self._stopwords:
                    freq[word] +=1
        return freq
    def summarize(self, article, n):
        text = article
        # title = article[1]
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        self._freq = self._compute_frequencies(word_sent)
        ranking = defaultdict(int)
        for i, sentence in enumerate(word_sent):
            for word in sentence:
                if word in self._freq:
                    ranking[i] += self.freq[word]
        sentences_index = nlargest(n, ranking, key=ranking.get)
        return [sentences[j] for j in sentences_index]


washingtonPostTechArticles = "https://www.washingtonpost.com/business/technology"
try:
    washingtonPostTechArticlesCorpus = scrapeSource(washingtonPostTechArticles, '2017', getwashingtonPostCorpus, 'article')
except:
    WPCorpus = readFile("corpus.txt")
    WPCorpusArray = WPCorpus.split("\n\n")

WPCorpus = readFile("corpus.txt")
WPCorpusArray = WPCorpus.split("\n\n")

# for techUrlDict in [washingtonPostTechArticlesCorpus]:
#     for articleUrl in techUrlDict:
#         if techUrlDict[articleUrl][1] is not None:
#             if len(techUrlDict[articleUrl][1]) >0:
#                 fs = FrequencySummarizer()
#                 summary = fs.extractFeatures(techUrlDict[articleUrl], 25)
#                 articleSummaries[articleUrl] = {'feature-vector': summary, 'label':'tech'}
for techArticle in WPCorpusArray:
    if len(techArticle) >0:
        fs = FrequencySummarizer()
        summary = fs.extractFeatures(techArticle, 25)
        techSummaryCorpus = readFile("techSummaryCorpus.txt")
        for word in summary:
            if word in techSummaryCorpus:
                writeInFile("", "techSummaryCorpus.txt")
            else:
                writeInFile(word, "techSummaryCorpus.txt")
print
