from django.db import models

class Release(models.Model):
    major = models.PositiveSmallIntegerField()
    minor = models.PositiveSmallIntegerField()
    patch = models.PositiveSmallIntegerField()
    show = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    scheduled = models.DateField(null=True, blank=True)
    description = models.TextField(default='', blank=True)

    class Meta:
        ordering = ('-major', '-minor', '-patch')
        unique_together = ('major', 'minor', 'patch')

    def __str__(self):
        return "%d.%d.%d" % (self.major, self.minor, self.patch)


class ReleaseItem(models.Model):
    TYPES = (
        ('B', 'bugfix'),
        ('F', 'feature'),
        ('O', 'other')
    )
    release = models.ForeignKey(Release, related_name='items')
    show = models.BooleanField(default=True)
    item_type = models.CharField(max_length=5, choices=TYPES)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.description
