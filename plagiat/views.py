from django.shortcuts import render


from .chiplagiat import *

from stop_words import get_stop_words


# Create your views here.

def index(request):
    context = dict()

    query = request.POST.get('query',None)

    if query:
        plagiarism = PlagiarismChecker(query,'fr')
        plagiat_results = plagiarism.get_plagiat_results()

        context['plagiat_results'] = plagiat_results
        context['query'] = query
        context['stopwords'] = get_stop_words('fr')

    return render(request, 'plagiat/index.html', context)
