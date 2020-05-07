from django.db import models

# Create your models here.

class AutoTestResult(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    SERIALNUMBER = models.CharField(max_length=100)
    GAME = models.CharField(max_length=100)
    INSTALL = models.CharField(max_length=100)
    ACTIVITY = models.CharField(max_length=100)
    LEVEL = models.CharField(max_length=100)
    RESULT = models.CharField(max_length=100)
    LOG = models.CharField(max_length=19999)
    REPORT = models.CharField(max_length=100)
    EXECUTOR = models.CharField(max_length=100)

    def __str__(self):
        return self.id


class AdbStatus(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    ADDRESS = models.CharField(max_length=100)
    INUSE = models.CharField(max_length=100)

    def __str__(self):
        return self.id


class Stress(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    TESTER = models.CharField(max_length=100)
    RESOLUTION = models.CharField(max_length=100)
    RETRY_IMAGE = models.CharField(max_length=100)
    PACKAGE = models.CharField(max_length=100)
    LEVEL = models.CharField(max_length=100)
    RUNTIME = models.CharField(max_length=100)

    def __str__(self):
        return self.id
