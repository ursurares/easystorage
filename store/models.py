from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from humanfriendly import format_size
from .validators import validate_file_size
import uuid
import os

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,help_text='Unique ID for this particular file across whole server')
    name=models.CharField(max_length=100,help_text='Filename')
    extension=models.CharField(max_length=10,help_text='Extension')
    date=models.DateTimeField(auto_now=True)
    owner=models.ForeignKey(User, on_delete=models.CASCADE)
    size=models.DecimalField(decimal_places=2,max_digits=5)

    class Meta:
        ordering = ['name','date']



    def __str__(self):
        return self.name+'.'+self.extension

def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'user_{0}/{1}'.format(instance.user.id, filename)
        
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

class Document(models.Model):
    user=models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    source= models.FileField(upload_to=get_file_path,validators=[validate_file_size])

    class Meta:
        ordering = ['title']

    @property
    def filename(self):
        return os.path.basename(self.source.name)
    @property
    def size(self):
        return self.source.size
    @property
    def url(self):
        return self.source.url
    @property
    def uploader(self):
        return self.user
    
    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        self.source.delete()
        super().delete(*args, **kwargs)