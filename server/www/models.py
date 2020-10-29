from django.db import models

# Create your models here.


from mongoengine import *
import datetime
class Choice(EmbeddedDocument):
    choice_text = StringField(max_length=200)
    votes = IntField(default=0)


class Poll(Document):
    question = StringField(max_length=200)
    pub_date = DateTimeField(help_text='date published')
    choices = ListField(EmbeddedDocumentField(Choice))
    
    meta = {
        'indexes': [
            'question', 
            ('pub_date', '+question')
        ]
    }
    
class BlogPost(Document):
    title = StringField(required=True, max_length=200)
    posted = DateTimeField(default=datetime.datetime.utcnow)
    tags = ListField(StringField(max_length=50))
    meta = {'allow_inheritance': True}
class TextPost(BlogPost):
    content = StringField(required=True)


