from django.db import models
from mongoengine import BooleanField, StringField, QuerySetManager, DateTimeField, ListField, EmbeddedDocumentField, EmbeddedDocument, Document
import datetime


class ImageInfo(EmbeddedDocument):
    public = BooleanField(default=True)
    sourceUrl = StringField(required=True)
    storePath = StringField(required=True)
    meta = {'collection': 'album', 'strict': False}


class ModelInfo(EmbeddedDocument):
    public = BooleanField(default=True)
    sourceUrl = StringField(required=True)
    imagePath = StringField()
    name = StringField(unique=True)
    displayName = StringField()
    birthday = StringField()
    birthPlace = StringField()
    age = StringField()
    nativeName = StringField()
    hobbies = ListField(StringField())
    heightMeasurements = StringField()
    about = StringField()
    meta = {'collection': 'album', 'strict': False}


class Album(Document):
    objects = QuerySetManager()
    title = StringField(required=True)
    source = StringField(required=True)
    idFromSource = StringField(required=True)
    albumId = StringField(required=True)
    url = StringField(required=True, unique=True)
    thumbnail = EmbeddedDocumentField(ImageInfo)
    modelName = StringField()
    modelDisplayName = StringField()
    createdDate = DateTimeField(default=datetime.datetime.utcnow)
    public = BooleanField(default=True)
    deleted = BooleanField()
    tags = ListField(StringField(max_length=2000))
    images = ListField(EmbeddedDocumentField(ImageInfo))

    content = ListField(StringField())
    meta = {'collection': 'album', 'strict': False}
