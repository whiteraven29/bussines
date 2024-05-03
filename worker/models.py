from django.db import models
from manager.models import Worker

class Item(models.Model):
    name = models.CharField(max_length=100)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ItemReport(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    laststock = models.IntegerField(default=0)
    present = models.IntegerField(default=0)
    consumed = models.IntegerField(default=0)
    entered = models.IntegerField(default=0)
    remaining = models.IntegerField(default=0)
    incomespent = models.FloatField(default=0)
    incomegained = models.FloatField(default=0)
    expenditures = models.FloatField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.item.name} on {self.date}"