from django.db import models

# Create your models here.

class AutoUITestResult(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=100)
    project = models.CharField(max_length=100)
    casename = models.CharField(max_length=100)
    runtime = models.CharField(max_length=100)
    resultwanted = models.CharField(max_length=100)
    resultinfact = models.CharField(max_length=100)
    testresult = models.CharField(max_length=100)
    costtime = models.CharField(max_length=100)
    log = models.TextField()
    report = models.CharField(max_length=1000)
    image = models.CharField(max_length=1000)
    date = models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)


class SubServer(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=100)
    server = models.CharField(max_length=50)
    single = models.CharField(max_length=1)
    status = models.CharField(max_length=1)

    def __str__(self):
        return self.id


class Task(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=100)
    project = models.CharField(max_length=50)
    platform = models.CharField(max_length=10)
    package = models.CharField(max_length=25)
    testcase = models.CharField(max_length=25)
    server = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    show = models.CharField(max_length=1)