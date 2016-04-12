from django.db import models

class XmlDump(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    dump = models.TextField()
    
    def __str__(self):
        return self.dump[:255]
