from flask import make_response, url_for
from feedgen.feed import FeedGenerator
from flask import Blueprint
from .models import get_active_jobs

feed = Blueprint('feed', __name__)

website = 'https://startupjobsportugal.com/'


@feed.get('/feed')
def rss():
    fg = FeedGenerator()
    fg.title('Startup Jobs Portugal')
    fg.description('Real-time feed for jobs at Startup Jobs Portugal.')
    fg.link(href='https://startupjobsportugal.com/')

    for job in get_active_jobs():
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


@feed.get('/feed/productized')
def rss_product():
    fg = FeedGenerator()
    fg.title('Startup Jobs Portugal')
    fg.description('Real-time feed for jobs at Startup Jobs Portugal.')
    fg.link(href='https://startupjobsportugal.com/')

    for job in get_active_jobs(category="product management"):
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
    fg.title('Startup Jobs Portugal')
    fg.description('Real-time feed for jobs at Startup Jobs Portugal.')
    fg.link(href='https://startupjobsportugal.com/')

    for job in get_active_jobs(category=category):

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
