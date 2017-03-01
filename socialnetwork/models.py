from __future__ import unicode_literals
import os
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    text = models.CharField(max_length = 160)
    user = models.ForeignKey(User, default=None) 
    messageTime = models.DateTimeField()

    def __unicode__(self):
        return unicode(self.text)

class Comment(models.Model):
    comm = models.CharField(max_length = 160)
    msg = models.ForeignKey(Message, default=None)
    time = models.DateTimeField()
    commenter = models.ForeignKey(User, default=None)

    def __unicode__(self):
        return unicode(self.comm)

class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
    photo = models.FileField(upload_to="images/", blank=True, null=True)
    firstname = models.CharField(max_length=40)
    lastname =  models.CharField(max_length=40)
    age = models.PositiveSmallIntegerField(blank=True, default=0)
    bio = models.TextField(max_length = 430, default="I'm cool")
    content_type = models.CharField(max_length=50)
    cool_people_to_follow = models.ManyToManyField("self")
    def __unicode__(self):
        return unicode(self.user.pk)