from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Worker(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class DailyReport(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    laststock = models.IntegerField()
    present = models.IntegerField()
    consumed = models.IntegerField()
    entered = models.IntegerField()
    remaining = models.IntegerField()
    incomespent = models.FloatField()
    incomegained=models.FloatField()
    expenditures = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.worker.firstname} {self.worker.lastname} on {self.date}"


@property
def income(self):
    return self.incomegained - self.incomespent

class Item(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
