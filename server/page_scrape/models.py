from django.db import models
from mongoengine import BooleanField, StringField, QuerySetManager, DateTimeField, ListField, EmbeddedDocumentField, EmbeddedDocument, Document
import datetime


class ImageInfo(EmbeddedDocument):
    public = BooleanField(default=True)
    sourceUrl = StringField(required=True)
    storePath = StringField()


class ModelInfo(EmbeddedDocument):
    public = BooleanField(default=True)
    sourceUrl = StringField(required=True)
    name = StringField(unique=True)
    displayName = StringField()
    birthday = StringField()
    birthPlace = StringField()
    age = StringField()
    hobbies = ListField(StringField())


class Album(Document):
    objects = QuerySetManager()
    title = StringField(required=True)
    source = StringField(required=True)
    idFromSource = StringField(required=True)

    url = StringField(required=True, unique=True)
    thumbnail = EmbeddedDocumentField(ImageInfo)
    modelName = StringField()
    createdDate = DateTimeField(default=datetime.datetime.utcnow)
    public = BooleanField(default=True)
    deleted = BooleanField()
    tags = ListField(StringField(max_length=2000))
    images = ListField(EmbeddedDocumentField(ImageInfo))

    content = ListField(StringField())
    meta = {'collection': 'album', 'strict': False}
