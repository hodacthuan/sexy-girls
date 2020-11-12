from django.db import models
import mongoengine
from mongoengine import BooleanField, StringField, QuerySetManager, DateTimeField, ListField, EmbeddedDocumentField, EmbeddedDocument, Document, IntField
import datetime


class ImageInfo(EmbeddedDocument):
    imgNo = StringField(required=True)
    imgIsPublic = BooleanField(default=True)
    imgSize = IntField(required=True)
    imgWidth = IntField(required=True)
    imgHeight = IntField(required=True)
    imgType = StringField(required=True)
    imgSourceUrl = StringField(required=True)
    imgStorePath = StringField(required=True)
    imgExtension = StringField(required=True)

    meta = {'collection': 'images', 'strict': False}


class ModelInfo(Document):
    objects = QuerySetManager()

    modelIsPublic = BooleanField(default=True)
    modelSource = StringField(required=True)
    modelName = StringField(unique=True)
    modelDisplayName = StringField()
    modelNativeName = StringField()
    modelProfession = StringField()
    modelReputation = IntField()
    modelRanking = IntField()
    modelCountry = StringField()
    modelAbout = ListField(StringField())
    modelType = StringField()
    modelSourceUrl = StringField(required=True)
    modelImage = EmbeddedDocumentField(ImageInfo)
    modelBirthday = StringField()
    modelBirthPlace = StringField()
    modelAge = StringField()
    modelSign = StringField()
    modelHobbies = ListField(StringField())
    modelHeightMeasurements = StringField()
    modelSocialInstagram = StringField()
    modelSocialFacebook = StringField()
    modelTags = ListField(StringField(max_length=2000))

    meta = {'collection': 'models', 'strict': False}


class Tag(Document):
    objects = QuerySetManager()

    tagTitle = StringField(required=True)
    tagDisplayTitle = StringField(required=True)
    tagIsPublic = BooleanField(default=True)
    tagThumbnail = ListField(StringField())
    tagType = StringField()

    meta = {'collection': 'tags', 'strict': False}


class Category(Document):
    objects = QuerySetManager()

    categoryTitle = StringField(required=True)
    categoryDisplayTitle = StringField(required=True)
    categoryIsPublic = BooleanField(default=True)
    categoryThumbnail = ListField(StringField())
    categoryType = StringField()

    meta = {'collection': 'categories', 'strict': False}


class Album(Document):
    objects = QuerySetManager()

    albumTitle = StringField(required=True)
    albumDisplayTitle = StringField(required=True)
    albumIsPublic = BooleanField(default=False)
    albumSource = StringField(required=True)
    albumSourceUrl = StringField(required=True, unique=True)
    albumSourceId = StringField()
    albumId = StringField()
    albumThumbnail = ListField(StringField(required=True))
    albumTags = ListField(StringField(max_length=2000))
    albumCategories = ListField(StringField(max_length=2000))
    albumImages = ListField(StringField(required=True))
    albumContent = ListField(StringField())
    albumModelName = StringField()
    albumModelId = StringField()
    albumUpdatedDate = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'albums', 'strict': False}
