from flask import make_response, url_for
from feedgen.feed import FeedGenerator
from flask import Blueprint
from .models import get_active_jobs

feed = Blueprint('feed', __name__)

website = 'https://fuzzboard.com/'

# TODO: Replace feed links with ('url_for') + _external=True


@feed.get('/feed')
def rss():
    fg = FeedGenerator()
    fg.title('Fuzzboard')
    fg.description('Real-time feed for startup jobs at Fuzzboard.')
    fg.link(href='https://fuzzboard.com/')

    for job in get_active_jobs(reverse=False):
        fe = fg.add_entry()
        fe.title(job['title'])
        fe.link(href=website + "jobs/" + job['slug'])
        fe.content(job['company'])
        fe.description(job['company'])
        fe.guid(str(job['_id']), permalink=False)
        fe.author(name='Fuzzboard')
        fe.pubDate(job['timestamp'])

    response = make_response(fg.rss_str())
    response.headers.set('Content-Type', 'application/rss+xml')

    return response


@feed.get('/feed/productized')
def rss_product():
    fg = FeedGenerator()
    fg.title('Fuzzboard')
    fg.description('Real-time feed for startup jobs at Fuzzboard.')
    fg.link(href='https://fuzzboard.com/')

    for job in get_active_jobs(category="product management", reverse=False):
        fe = fg.add_entry()
        fe.title(job['title'])
        fe.link(href=website + "jobs/" + job['slug'])
        fe.content(job['company'])
        fe.description(job['company'])
        fe.guid(str(job['_id']), permalink=False)
        fe.author(name='Startup Jobs Portugal')
        fe.pubDate(job['timestamp'])

    response = make_response(fg.rss_str())
    response.headers.set('Content-Type', 'application/rss+xml')

    return response


@feed.get('/feed/<category>')
def rss_all(category):
    fg = FeedGenerator()
    fg.title('Fuzzboard')
    fg.description('Real-time feed for startup jobs at Fuzzboard.')
    fg.link(href='https://fuzzboard.com/')

    for job in get_active_jobs(category=category, reverse=False):

        fe = fg.add_entry()

        fe.title(job['title'])
        fe.link(href=website + "jobs/" + job['slug'])
        fe.content(job['company'])
        fe.description(job['company'])
        fe.guid(str(job['_id']), permalink=False)
        fe.author(name='Startup Jobs Portugal')
        fe.pubDate(job['timestamp'])

    response = make_response(fg.rss_str())
    response.headers.set('Content-Type', 'application/rss+xml')

    return response

# Casafari VISA Ukraine Feed Start


@feed.get('/feed/visa')
def rss_visa():
    fg = FeedGenerator()
    fg.title('Fuzzboard: Jobs for anyone escaping the war.')
    fg.description('Real-time feed with jobs for anyone escaping the war.')
    fg.link(href='https://fuzzboard.com/')

    for job in get_active_jobs(visa_sponsor=True, reverse=False):
        fe = fg.add_entry()
        fe.title(job['title'])
        fe.link(href=website + "jobs/" + job['slug'])
        fe.content(job['company'])
        fe.description(job['company'])
        fe.guid(str(job['_id']), permalink=False)
        fe.author(name='Startup Jobs Portugal')
        fe.pubDate(job['timestamp'])

    response = make_response(fg.rss_str())
    response.headers.set('Content-Type', 'application/rss+xml')

    return response


@feed.get('/feed/visa/<category>')
def rss_visa_all(category):
    fg = FeedGenerator()
    fg.title('Fuzzboard: Jobs for anyone escaping the war.')
    fg.description('Real-time feed with jobs for anyone escaping the war.')
    fg.link(href='https://fuzzboard.com/')

    for job in get_active_jobs(category=category, visa_sponsor=True, reverse=False):

        fe = fg.add_entry()

        fe.title(job['title'])
        fe.link(href=website + "jobs/" + job['slug'])
        fe.content(job['company'])
        fe.description(job['company'])
        fe.guid(str(job['_id']), permalink=False)
        fe.author(name='Fuzzboard')
        fe.pubDate(job['timestamp'])

    response = make_response(fg.rss_str())
    response.headers.set('Content-Type', 'application/rss+xml')

    return response
