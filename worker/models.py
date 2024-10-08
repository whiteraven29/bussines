from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission
from manager.models import Branch
from django.utils import timezone

class Worker(AbstractUser):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='workers')
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    # Add other fields if necessary
    groups = models.ManyToManyField(
        Group,
        related_name='worker_set',  # Changed from 'user_set' to 'worker_set'
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='worker_user_permissions',  # Changed from 'user_set' to 'worker_user_permissions'
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    def manager_name(self):
        return self.branch.manager.username if self.branch and self.branch.manager else 'No Manager'
    
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.branch.name})"
    class Meta:
        verbose_name = 'Worker'
        verbose_name_plural = 'Workers'    
  
class Item(models.Model):
    name = models.CharField(max_length=100)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ItemReport(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    laststock = models.IntegerField(default=0)
    addedstock = models.IntegerField(default=0)
    currentstock = models.IntegerField(default=0)
    consumed = models.IntegerField(default=0)
    remaining = models.IntegerField(default=0)
    incomespent = models.FloatField(default=0)
    incomegained = models.FloatField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Report for {self.item.name} on {self.date}"
    
class DailyExpenditure(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    expenditure = models.FloatField()

    class Meta:
        unique_together = ('branch', 'date')

    def __str__(self):
        return f"{self.branch.name} - {self.date}: {self.expenditure}"    
