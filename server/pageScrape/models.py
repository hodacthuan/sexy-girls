from django.db import models
from mongoengine import BooleanField, StringField, QuerySetManager, DateTimeField, ListField, EmbeddedDocumentField, EmbeddedDocument, Document
import datetime


class ImageInfo(EmbeddedDocument):
    imgIsPublic = BooleanField(default=True)
    imgSourceUrl = StringField(required=True)
    imgStorePath = StringField(required=True)
    meta = {'collection': 'album', 'strict': False}


class ModelInfo(EmbeddedDocument):
    modelIsPublic = BooleanField(default=True)
    modelSourceUrl = StringField(required=True)
    modelImagePath = StringField()
    modelName = StringField(unique=True)
    modelDisplayName = StringField()
    modelBirthday = StringField()
    modelBirthPlace = StringField()
    modelAge = StringField()
    modelNativeName = StringField()
    modelHobbies = ListField(StringField())
    modelHeightMeasurements = StringField()
    modelAbout = StringField()
    meta = {'collection': 'album', 'strict': False}


class Album(Document):
    objects = QuerySetManager()
    albumTitle = StringField(required=True)
    albumIsPublic = BooleanField(default=True)
    albumSource = StringField(required=True)
    albumIdFromSource = StringField(required=True)
    albumId = StringField(required=True)
    albumSourceUrl = StringField(required=True, unique=True)
    albumThumbnail = EmbeddedDocumentField(ImageInfo)
    albumTags = ListField(StringField(max_length=2000))
    albumImages = ListField(EmbeddedDocumentField(ImageInfo))
    albumContent = ListField(StringField())
    modelName = StringField()
    modelDisplayName = StringField()
    createdDate = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'album', 'strict': False}
