from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from pytz import timezone as timezonePYTZ
import os

# Custom Filename & Save Path #
def subforumIconImagePath(instance, filename):
    return os.path.join('subforum_icon', filename)
    
# Delete Existing Profile Pictures #
class SubforumIconOverwriteStorage(FileSystemStorage):

    def _save(self, name, content):
        for filename in os.listdir(settings.MEDIA_ROOT + '/subforum_icon'):
            if filename.split('.')[0].lower() == name.split("\\")[1].split('.')[0].lower():
                self.delete('subforum_icon/' + filename)
                
        return super(SubforumIconOverwriteStorage, self)._save(name, content)
            
    def get_available_name(self, name, max_length=None):
        return name
    
class Subforum(models.Model):
    titleURL = models.CharField(unique=True, max_length=256)
    title = models.CharField(max_length=256)
    description = models.CharField(default="Default Description", max_length=256)
    image = models.ImageField(default='subforum_icon/default.png', upload_to=subforumIconImagePath, storage=SubforumIconOverwriteStorage)
    
    def __str__(self):
        return self.title
        
    def threadCount(self):
        return len(Thread.objects.filter(subforum=self))

class Thread(models.Model):
    subforum = models.ForeignKey(Subforum, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=256)
    viewCount = models.IntegerField(default=0)
    isLocked = models.BooleanField(default=False)
    date_posted = models.DateTimeField(default=timezone.now)
    last_post_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return str(self.id) + " - " + self.title
        
    def getTitle(self):
        title = self.title
        if self.isLocked:
            title = title + " (Locked)"
        return title
        
    def replyCount(self):
        return len(Post.objects.filter(subforum=self.subforum, thread=self)) - 1
        
    def lastDatePosted(self):
        return Post.objects.filter(subforum=self.subforum, thread=self).last().date_posted
    
class Post(models.Model):
    subforum = models.ForeignKey(Subforum, on_delete=models.SET_NULL, null=True)
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return str(self.id) + " - " + self.content[0:50]
        
    def getDateString(self):
        
        # Format - YYYYMMDDHHMM #
        timeString = str(self.date_posted.astimezone(timezonePYTZ("US/Eastern")))
        postDate = str(timeString).split(' ')[0]
        postTime = str(timeString).split(' ')[1][0:8].replace(':', '-')
        dateTimeString = str(postDate + postTime).replace('-', '')
        
        return dateTimeString
        