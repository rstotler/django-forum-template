from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from PIL import Image
import os

# Custom Filename & Save Path #
def profileImagePath(instance, filename):
    uploadTo = 'profile_pics'
    ext = filename.split('.')[-1]
    filename = instance.user.username
    
    return os.path.join(uploadTo, filename + '.' + ext)
    
# Delete Existing Profile Pictures #
class ProfileOverwriteStorage(FileSystemStorage):

    def _save(self, name, content):
        for filename in os.listdir(settings.MEDIA_ROOT + '/profile_pics'):
            if filename.split('.')[0].lower() == name.split("\\")[1].split('.')[0].lower():
                self.delete('profile_pics/' + filename)
                
        return super(ProfileOverwriteStorage, self)._save(name, content)
            
    def get_available_name(self, name, max_length=None):
        return name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to=profileImagePath, storage=ProfileOverwriteStorage)
    userLevel = models.IntegerField(default=1)
    usernameChangeCount = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.user.username} Profile'
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
            
    def getPostCount(self):
        return len(self.user.post_set.all())

class Message(models.Model):
    #sender = models.ForeignKey, on_delete=models.SET_NULL, null=True)
    #receiver = models.ForeignKey, on_delete=models.SET_NULL, null=True)
    #date_sent = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=256)
    content = models.TextField()
    