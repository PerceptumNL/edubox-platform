from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, \
        HttpResponseServerError, HttpResponseRedirect
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import django.dispatch

import operator
import datetime
import re
import json
import requests

from .models import *
from services.events.models import Event, ReadEvent, RatedEvent, ScoredEvent, ClickedEvent
from loader.models import App
from loader.helpers import dispatch_service_request, get_current_app_id

def update_feeds(request):
    for feed in ContentFeed.objects.all():
        feed.update_feed()
    return HttpResponse()

@login_required
def article_overview(request):
    """Return response containing overview of categories and articles."""
    # Only show top categories on the index page
    categories = Category.objects.filter(parent=None).order_by('order')
    return render(request, 'article_overview.html', {
        "categories": categories
    })

@login_required
def index(request):
    """Return response containing overview of categories and articles."""
    # Only show top categories on the index page
    categories = Category.objects.filter(parent=None)
    articles = []
    for category in categories:
        articles += category.get_articles()
    # Render response
    if request.is_ajax():
        # Return JSON list of categories with their properties
        categories = [{'url': c.get_absolute_url(), 'title': c.title,
            'image': c.image} for c in categories]
        articles = [{'url': a.get_absolute_url(), 'title': a.title,
            'image': a.image} for a in articles]
        return HttpResponse(
                json.dumps({'categories': categories, 'articles': articles}),
                content_type='application/json')
    else:
        # Render HTML of the landing page containing top categories
        return render(request, 'article_overview.html',{
                "articles": articles,
                "categories": categories})

@login_required
def query(request):
    """Return response containing articles matching the query."""
    query_string = request.GET.get('q', None)
    if query_string is None:
        # Fetch any subcategories and articles contained in the category.
        articles = []
        for article in TimestampedArticle.objects.order_by('-publication_date').all()[:50]:
            category = article.get_categories()[0]
            articles.append({
                'url': article.get_absolute_url(),
                'title': article.title,
                'category-color': category.color,
                'image': article.image if article.image else category.image})
        return HttpResponse(json.dumps({'articles': articles}), content_type='application/json')
    elif query_string.strip():
        matching = []
        articles = []
        querylist = [Q(body__icontains=query) for query in normalize_query(query_string)]
        querylist += [Q(title__icontains=query) for query in normalize_query(query_string)]
        matching = TimestampedArticle.objects.filter(reduce(operator.or_, querylist))
        matching = sorted(matching, key=lambda x: x.publication_date,
                reverse=True)
        for article in matching:
            articles.append({
                'url': article.get_absolute_url(),
                'title': article.title,
                'category-color': article.categories.all().first().color,
                'image': article.image if article.image else article.categories.all().first().image})
        return HttpResponse(json.dumps({'articles': articles}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'articles': []}), content_type="application/json")

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

@login_required
def category(request, identifier, source='local'):
    """Return response containing contents of identified category.

    The category is identified by a identifier and optionally a source. When
    the source is set to 'local', the identifier must be the primary key of a
    Category object. When the source is set to 'wikipedia', the identifier must
    correspond to either a pageid or a title of a wikipedia page.

    Named keywords:
    identifier -- Number or string identifying the category
    source -- The source the identifier belongs to ( default 'local' )
    """
    if not request.is_ajax():
        return HttpResponseRedirect('/')
    try:
        category = Category.objects.get(pk=int(identifier))
    except Category.DoesNotExist:
        return HttpResponseRedirect('/')
    # Fetch any subcategories and articles contained in the category.
    articles = []
    for article in category.get_articles():
        d = {'url': article.get_absolute_url(),
            'title': article.title,
            'category-color': category.color,
            'image': article.image if article.image else category.image,
            'publication_date': str(article.publication_date)
        }
        articles.append(d)
    subcategories = [{'url': c.get_absolute_url(), 'title': c.title,
        'image': c.image} for c in category.get_subcategories()]
    # Return JSON list of topics with their properties
    return HttpResponse(json.dumps({'articles': articles,
            'subcategories': subcategories}), content_type='application/json')

@login_required
def article(request, identifier):
    """Return response containing the identified article.

    The article is identified by a identifier and optionally a source. When
    the source is set to 'local', the identifier must be the primary key of a
    Category object. When the source is set to 'wikipedia', the identifier must
    correspond to either a pageid or a title of a wikipedia page.

    Named keywords:
    identifier -- Number or string identifying the category
    source -- The source the identifier belongs to ( default 'local' )
    """
    # Resolve identified article
    try:
        # Attempt to retrieve the article
        article = TimestampedArticle.objects.get(pk=int(identifier))
    except TimestampedArticle.DoesNotExist:
        return HttpResponseRedirect('/')

    # Retrieve the categories that this article belongs to.
    categories = article.get_categories()

    if not request.is_ajax():
        # Fetch random articles from the same categories for reading suggestions.
        random_articles = []
        read_articles = ReadEvent.objects.filter(user=request.user)
        read_articles = list(set([history.article.pk for history in read_articles] + [article.pk]))
        for category in categories:
            random_articles += category.get_random_articles(3, read_articles)

        # Ensure the current article is not suggested again
        if article in random_articles:
            random_articles.remove(article)

        difficulty_items = ScoredEvent.objects.filter(user=request.user, article=article)
        rating_items = RatedEvent.objects.filter(user=request.user, article=article)

        recommendations = []
        for rand_article in random_articles:
            if rand_article.image:
                recommendations.append(rand_article)

        # For all categories this article belongs to
        for category in categories:
            # If the category was stored in the database
            if category.pk is not None:
                # Store read event in the Event store
                response = dispatch_service_request(request,
                        method="POST",
                        url="service:events/api/",
                        json = {
                            'app':  get_current_app_id(request),
                            'group': '',
                            'user': request.user.pk,
                            'verb': 'read',
                            'obj': identifier
                        })
                import q; q.d()

        return render(request, 'article_page.html', {
            "article": article,
            "random_articles": recommendations,
            "rating_given": len(rating_items)>0,
            "difficulty_given": len(difficulty_items)>0
        })
    else:
        # Return JSON with article properties
        date = article.publication_date.strftime('%d-%m-%Y %H:%M')

        return HttpResponse(
            json.dumps({
                'title': article.title,
                'date': date,
                'image': article.image,
                'body': article.get_body()
            }),
            content_type='application/json')
