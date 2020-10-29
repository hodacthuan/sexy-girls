from django.db import models

from mongoengine import *
import datetime


class ImageInfo(EmbeddedDocument):
    publish = BooleanField()
    sourceUrl =StringField()
    storeUrl = StringField()


class Post(Document):
    objects = QuerySetManager()
    title = StringField(required=True)
    source = StringField(required=True)
    
    url = StringField(required=True,unique=True)
    thumbnail = StringField()
    postedDate = DateTimeField(default=datetime.datetime.utcnow)
    publish = BooleanField()
    deleted = BooleanField()
    tags = ListField(StringField(max_length=2000))
    images = ListField(EmbeddedDocumentField(ImageInfo))
    
    content = StringField()




