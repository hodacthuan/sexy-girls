import os

MONGODB_URL = os.environ['MONGODB_URL']
AWS_BUCKET = os.environ['AWS_BUCKET']
BUCKET_PUBLIC_URL = os.environ['BUCKET_PUBLIC_URL']
AWS_ACCESS_KEY = os.environ['ADMIN_ACCESS_KEY_ID']
AWS_SECRET_KEY = os.environ['ADMIN_SECRET_ACCESS_KEY']
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

IMAGE_STORAGE = os.path.join(os.path.dirname(
    __file__), '../tempStorages/images/')
THUMBNAIL_STORAGE = os.path.join(os.path.dirname(
    __file__), '../tempStorages/thumbnails/')

USER_AGENT_HEADER = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'

ALBUM_PAGINATION_NUMBER_OF_IMAGE = 10
DEPLOY_ENV = 'local'
if os.environ.get('DEPLOY_ENV') is not None:
    DEPLOY_ENV = os.environ['DEPLOY_ENV']

IMAGE_HOST = os.environ['LOCAL_IMAGE_HOST']
if DEPLOY_ENV == 'prod':
    IMAGE_HOST = os.environ['PROD_IMAGE_HOST']
