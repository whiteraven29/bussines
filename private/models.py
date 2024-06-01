from django.db import models

from django.db import models

class Single(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)  # Define is_active field
    is_staff = models.BooleanField(default=False)  # Define is_staff field

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
