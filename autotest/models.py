from django.db import models

# Create your models here.

class AutoUITestResult(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=20)
    project = models.CharField(max_length=50)
    casename = models.CharField(max_length=100)
    runtime = models.CharField(max_length=25)
    resultwanted = models.CharField(max_length=1000)
    resultinfact = models.CharField(max_length=1000)
    testresult = models.CharField(max_length=10)
    costtime = models.CharField(max_length=10)
    log = models.TextField()
    report = models.CharField(max_length=1000)
    image = models.CharField(max_length=1000)
    date = models.CharField(max_length=25)

    def __str__(self):
        return str(self.id)


class SubServer(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=100)
    server = models.CharField(max_length=50)
    single = models.CharField(max_length=1)
    status = models.CharField(max_length=1)

    def __str__(self):
        return str(self.id)


class Task(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=20)
    project = models.CharField(max_length=50)
    platform = models.CharField(max_length=10)
    package = models.CharField(max_length=25)
    testcase = models.CharField(max_length=25)
    server = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    show = models.CharField(max_length=1)
    executetime = models.CharField(max_length=25)

    def __str__(self):
        return str(self.id)


class Log(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=20)
    logname = models.CharField(max_length=20)
    recordtime = models.CharField(max_length=25)
    data = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.id)