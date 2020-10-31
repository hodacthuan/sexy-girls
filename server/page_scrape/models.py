from django.db import models

from mongoengine import *
import datetime


class ImageInfo(EmbeddedDocument):
    public = BooleanField(default=True)
    sourceUrl = StringField(required=True)
    storePath = StringField()


class ModelInfo(EmbeddedDocument):
    public = BooleanField(default=True)
    sourceUrl = StringField(required=True)
    name = StringField()


class Album(Document):
    objects = QuerySetManager()
    title = StringField(required=True)
    source = StringField(required=True)
    idFromSource = StringField()

    url = StringField(required=True, unique=True)
    thumbnail = EmbeddedDocumentField(ImageInfo)
    postedDate = DateTimeField(default=datetime.datetime.utcnow)
    public = BooleanField(default=True)
    deleted = BooleanField()
    tags = ListField(StringField(max_length=2000))
    images = ListField(EmbeddedDocumentField(ImageInfo))

    content = ListField(StringField())
