import os
from pathlib import Path
from dotenv import load_dotenv

envPath = os.path.dirname(__file__)+'/../.'+'./devops/'
envFile = Path(envPath + 'secrets.env')
load_dotenv(dotenv_path=envFile)

DEPLOY_ENV = 'local'
if os.environ.get('DEPLOY_ENV') is not None:
    DEPLOY_ENV = os.environ['DEPLOY_ENV']

envFile = Path(envPath + DEPLOY_ENV + '.env')
load_dotenv(dotenv_path=envFile)

MONGODB_URL = os.environ['MONGODB_URL']
AWS_BUCKET = os.environ['AWS_BUCKET']
BUCKET_PUBLIC_URL = os.environ['BUCKET_PUBLIC_URL']
AWS_ACCESS_KEY = os.environ['ADMIN_ACCESS_KEY_ID']
AWS_SECRET_KEY = os.environ['ADMIN_SECRET_ACCESS_KEY']
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
REDISDB_URL = os.environ['REDISDB_URL']
REDISDB_PASSWORD = os.environ['REDISDB_PASSWORD']
REDISDB_SERVER = os.environ['REDISDB_SERVER']
REDISDB_PORT = os.environ['REDISDB_PORT']
REDISDB_DBNUMBER = os.environ['REDISDB_DBNUMBER']
IMAGE_HOST = os.environ['IMAGE_HOST']
REGISTER_TOKEN = os.environ['REGISTER_TOKEN']

IMAGE_STORAGE = os.path.join(os.path.dirname(
    __file__), '../tempStorages/images/')
THUMBNAIL_STORAGE = os.path.join(os.path.dirname(
    __file__), '../tempStorages/thumbnails/')

USER_AGENT_HEADER = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'

ALBUM_PAGINATION_NUMBER_OF_IMAGE = 10
MAX_IMAGES_IN_ONE_PAGE = 32
