import re, math
import urllib.request
from bs4 import BeautifulSoup, Comment
from collections import Counter
from stop_words import get_stop_words
from googlesearch import search as google_search
import urllib.error


class PlagiarismChecker():
    google_search_max_results = 5
    stopwords = get_stop_words('fr')
    #urls_details = []  #

    """
    url_details is composed of dictionnaries
    { 
        'url': string  ,
        'data' : {
                'html': 'html_data' ,
                'text' : 'html_text',
                'keywords' = [],
                'similarity' : float 
           },
        
    }
    """

    def __init__(self, query, language):
        self.query = query
        self.language = language
        self.urls_details = []

    def get_google_urls(self):
        urls = google_search(self.query, stop=self.google_search_max_results)
        return urls

    def get_urls_text(self):
        for url in self.get_google_urls():
            url_details = {
                'url': url,
                'data': get_page_data(self.query,url),
            }
            self.urls_details.append(url_details)

    def get_plagiat_results(self):
        self.get_urls_text()
        return self.urls_details




def discover_google_plagiat(query):
    # stop  à 20 liens pour ne pas être trop long
    urls = google_search(query, stop=20)


def get_page_soup(url):
    if url.endswith(".pdf"):
        return Exception("La  page demandée est  en pdf")
    else:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req)
        soup = BeautifulSoup(html)

        # Remove comments in html   <!-- comment content  -->
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

        return soup


def get_page_text(url):
    page_html = get_page_soup(url)
    page_html = page_html.findAll(text=True)
    result = filter(visible, page_html)
    return ' '.join(list(result))


def get_page_data(query,url):
    if url.endswith('.pdf'):
        return

    try:
        html = get_page_soup(url)
        html_page = ','.join(str(v) for v in html.find('body').findChildren())
        html = html.findAll(text=True)
    except urllib.error.HTTPError as e:
        print(e.__dict__)
        return
    except urllib.error.URLError as e:
        print(e.__dict__)
        return

    result = filter(visible, html)
    text = ' '.join(list(result))

    text_keywords =  get_text_without_stop_words(text).lower()
    query =  get_text_without_stop_words(query).lower()

    jaccard_sim = get_jaccard_similarity(query,text_keywords)

    similarity = jaccard_sim['similarity']
    intersection_keywords = jaccard_sim['keywords']

    return {'html': html,'html_page': html_page, 'text': text, 'keywords': intersection_keywords, 'similarity': similarity}


def get_jaccard_similarity(query, document):
    # You have to do this before calling this method :
    # query = get_text_without_stop_words(query).lower()
    # document = get_text_without_stop_words(document).lower()

    a = set(query.split())
    b = set(document.split())
    c = a.intersection(b)

    # Document similarity to Query
    #similarity = round((float(len(c)) / (len(a) + len(b) - len(c))), 2)
    #sim2 = round((1 - similarity), 2) * 100

    similarity = (len(c) * 100) / len(a)

    return {'similarity':similarity, 'keywords':c}


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    print(intersection)

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    print(numerator)
    print(denominator)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


WORD = re.compile(r'\w+')


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)


def get_cosine_similarity(query, document):
    query = get_text_without_stop_words(query)
    document = get_text_without_stop_words(document)

    vector1 = text_to_vector(query)
    vector2 = text_to_vector(document)

    cosine = get_cosine(vector1, vector2)

    print('Cosine:' + str(cosine))
    return cosine


def get_text_without_stop_words(text):
    stopwords = get_stop_words('fr')
    querywords = text.split()

    resultwords = [word for word in querywords if word.lower() not in stopwords]
    result = ' '.join(resultwords)

    return result


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

#
# print (list(result))
