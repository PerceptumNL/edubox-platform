from django.db import models

class XmlDump(models.Model):
    dump = models.TextField()
    
    def __str__(self):
        return self.dump[:255]
