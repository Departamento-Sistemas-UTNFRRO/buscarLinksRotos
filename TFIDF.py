# Codigo original tomado de https://github.com/bitemyapp/tf-idf-1

import math


class Tokenizer:
    @staticmethod
    def tokenize(document):
        def removeNonAscii(s):
            """ Remove non ascii chars from a string """
            return "".join(i for i in s if ord(i) < 128)

        tokens = [t.lower() for t in document.split()]
        result = map(lambda x: removeNonAscii(x), tokens)
        return list(result)


class DocumentLink(object):
    def __init__(self, linkUrl):
        self.Link = linkUrl
        self.Document = self._convertLinkToDocument(linkUrl)
        self.DocumentTokens = Tokenizer.tokenize(self.Document)
        self.DocumentTokensCount = len(self.DocumentTokens)

    def _convertLinkToDocument(self, link):
        link = link.replace('http://', ' ')
        link = link.replace('https://', ' ')
        link = link.replace('.html', ' ')
        link = link.replace('www', ' ')
        link = link.replace('/', ' ')
        link = link.replace('&', ' ')
        link = link.replace('=', ' ')
        link = link.replace('.', ' ')
        link = link.replace('-', ' ')
        link = link.replace('_', ' ')
        return link


class TfIdf:

    def __init__(self, documents=None):
        self.documents = documents

    # FIXME: para a la clase documento esto
    def word_frequency(self, word, tokens):
        """ How many times does a word appear in a document? """
        return tokens.count(word)

    def document_term_frequency(self, term, document):
        return self.word_frequency(term, document.DocumentTokens)

    def tf(self, term, document):
        word_count = document.DocumentTokensCount
        term_occurs = self.document_term_frequency(term, document)
        return term_occurs / float(word_count)

    def docs_containing_term(self, term, documents):
        """ Returns the number of documents that contain a term """
        def term_occurs(term, document):
            count = self.document_term_frequency(term, document)
            if (count > 0):
                return 1
            else:
                return 0
        occurs = [term_occurs(term, d.Document) for d in documents]
        return sum(occurs)

    def idf(self, term, documents):
        "General importance of the term across document collection"
        occurences = self.docs_containing_term(term, documents)
        return math.log(len(documents) / 1 + occurences)

    def tf_idf(self, word, document, documents):
        """ Returns the tf-idf score. A high weight of the tf-idf calculation
            is reached when you have a high term frequency (tf) in the given document (local parameter)
            and a low document frequency of the term in the whole collection (global parameter) """
        return self.tf(word, document.Document) * self.idf(word, documents)

    def generateDocumentRanking(self, doc_list, Term):
        """Return orderer ranking based on search term"""
        ranking = {}
        tokens = Tokenizer.tokenize(Term)
        for d in doc_list:
            tdidf = 0.0
            for token in tokens:
                tdidf = tdidf + self.tf_idf(token, d, doc_list)
            ranking[d] = tdidf
        return ranking

    def cleanDocument(self, link):
        link = link.replace('/', ' ')
        link = link.replace('&', ' ')
        link = link.replace('=', ' ')
        link = link.replace('.', ' ')
        link = link.replace('-', ' ')
        link = link.replace('_', ' ')
        link = link.replace('"', ' ')
        return link

    def getNearestLinkToTerm(self, linklist, titulo_post):
        doc_list = []
        for l in linklist:
            doc_list.append(DocumentLink(l))

        titulo_post = self.cleanDocument(titulo_post)

        ranking = self.generateDocumentRanking(doc_list, titulo_post)
        ranking = sorted(ranking.items(), key=lambda t: t[1], reverse=True)
        nearestDocument = ranking[0]
        if nearestDocument[1] == 0.0:
            return None
        return nearestDocument[0].Link
