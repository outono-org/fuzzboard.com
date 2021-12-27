from flask import make_response
from feedgen.feed import FeedGenerator
from flask import Blueprint
from .models import get_active_jobs, get_active_jobs2

feed = Blueprint('feed', __name__)


@feed.get('/feed')
def rss():
    fg = FeedGenerator()
    fg.title('Startup Jobs Portugal')
    fg.description('Real-time feed for jobs at Startup Jobs Portugal.')
    fg.link(href='https://startupjobsportugal.com/')

    for job in get_active_jobs2():
        fe = fg.add_entry()
        fe.title(job['title'])
        fe.link(href=job['url'])
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

    for job in get_active_jobs("product management"):
        fe = fg.add_entry()
        fe.title(job['title'])
        fe.link(href=job['url'])
        fe.content(job['company'])
        fe.description(job['company'])
        fe.guid(str(job['_id']), permalink=False)
        fe.author(name='Startup Jobs Portugal')
        fe.pubDate(job['timestamp'])

    response = make_response(fg.rss_str())
    response.headers.set('Content-Type', 'application/rss+xml')

    return response
