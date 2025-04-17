from django.db import models

# Create your models here.
class Po(models.Model):
    name = models.CharField(max_length=100)
    password = models.EmailField(max_length=100)
   

    def __str__(self):
        return self.name