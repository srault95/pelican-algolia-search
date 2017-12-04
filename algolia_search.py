import hashlib
from pprint import pprint

import logging

from bs4 import BeautifulSoup

from pelican import signals
from pelican.settings import DEFAULT_CONFIG
from algoliasearch import algoliasearch

logger = logging.getLogger(__name__)

__all__ = ['register']

def set_default_settings(settings):
    settings.setdefault('ALGOLIA_APP_ID', None)
    settings.setdefault('ALGOLIA_SEARCH_API_KEY', None)
    settings.setdefault('ALGOLIA_ADMIN_API_KEY', None)
    settings.setdefault('ALGOLIA_INDEX_NAME', 'blog')

def init_default_config(pelican):
    set_default_settings(DEFAULT_CONFIG)
    if(pelican):
        set_default_settings(pelican.settings)

def convert_article(page):

    soup_title = BeautifulSoup(page.title.replace('&nbsp;', ' '), 'html.parser')
    page_title = soup_title.get_text(' ', strip=True).replace('“', '"').replace('”', '"').replace('’', "'").replace('^', '&#94;')

    soup_text = BeautifulSoup(page.content, 'html.parser')
    page_text = soup_text.get_text(' ', strip=True).replace('“', '"').replace('”', '"').replace('’', "'").replace('¶', ' ').replace('^', '&#94;')
    page_text = ' '.join(page_text.split())

    soup_summary = BeautifulSoup(page.summary, 'html.parser')
    page_summary = soup_summary.get_text(' ', strip=True).replace('“', '"').replace('”', '"').replace('’', "'").replace('¶', ' ').replace('^', '&#94;')

    if getattr(page, 'category', 'None') == 'None':
        page_category = ''
    else:
        page_category = page.category.name

    #siteurl = page.settings.get('SITEURL')
    #page_url = siteurl + '/' + page.url
    page_url = page.url

    tags = [t.name for t in getattr(page, "tags", [])]

    page_created = page.date
    page_modified = getattr(page, 'modified', None)
    page_date = page_created
    if page_modified:
        page_date = page_modified

    return {
        'slug': page.slug,
        'date': page_date,
        'created': page_created,
        'modified': page_modified,
        'title': page_title,
        'category': page_category,
        'content': page_text,
        'summary': page_summary,
        'tags': tags,
        'url': page_url
    }

def index_generator(generator):
    index_name = generator.settings.get('ALGOLIA_INDEX_NAME', None)
    app_id = generator.settings.get('ALGOLIA_APP_ID', None)
    admin_api_key = generator.settings.get('ALGOLIA_ADMIN_API_KEY', None)

    if None in [index_name, app_id, admin_api_key]:
        logger.error("Algolia Indexe - settings error")
        return

    logger.info("Generating Algolia index '%s' for %d articles..." % (index_name, len(generator.articles)))

    client = algoliasearch.Client(app_id, admin_api_key)
    index = client.init_index(index_name)

    #TODO: utiliser flag dans metadata pour bypass search
    #TODO: settings sur fields

    pprint(index.get_settings())

    common_settings = {
        'maxFacetHits': 20,
        'attributesToRetrieve': [
            'title',
            'summary',
            'content',
            'url',
            'created',
            'modified',
            'tags'
        ],
        'attributesToHighlight': [
            'title',
            'summary',
        ],
        'searchableAttributes': [
            'title',
            'summary',
            'content',
        ],
        'attributesForFaceting': [
            'tags',
        ],
    }

    settings = common_settings.copy()
    settings.update({
        "replicas": [
            "blog_created_asc",
            "blog_title_asc",
            #"blog_created_desc",
        ],
        "ranking": [
            "desc(created)",
        ]
    })
    index.set_settings(settings)

    blog_created_asc = client.init_index("blog_created_asc")
    settings = common_settings.copy()
    settings.update({
        "ranking": [
            "asc(created)",
        ]
    })
    blog_created_asc.set_settings(settings)

    blog_title_asc = client.init_index("blog_title_asc")
    settings = common_settings.copy()
    settings.update({
        "ranking": [
            "asc(title)",
        ]
    })
    blog_title_asc.set_settings(settings)

    exists = []

    for article in generator.articles:
        try:
            logger.info("Indexing article: '%s'" % article.title)
            data = convert_article(article)
            objectId = hashlib.sha256(str(article.slug).encode('utf-8')).hexdigest()
            exists.append(objectId)
            index.add_object(data, objectId)
        except Exception as err:
            logger.error(err)

    logger.info('Purge old Algolia objects')
    for_delete = []
    res = index.browse_all()
    for hit in res:
        if not hit['objectID'] in exists:
            for_delete.append(hit['objectID'])
            logger.debug('Delete old article[%s]' % hit['title'])

    if for_delete:
        res = index.delete_objects(for_delete)
        #print(res)
        #{'objectIDs': ['ec5df277195755d82b8cbc3dedb4088ece38cece2ce935990373ef4dc4d83550'], 'taskID': 314782891}

def register():
    signals.initialized.connect(init_default_config)
    signals.article_generator_finalized.connect(index_generator)
