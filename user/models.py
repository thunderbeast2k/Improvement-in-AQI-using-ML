from django.db import models

# Create your models here.
class user_reg(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=300)
    email = models.CharField(max_length=200)
    mobile = models.CharField(max_length=200)
    uname = models.CharField(max_length=200)
    password = models.CharField(max_length=300)

class view_dataset(models.Model):
    id = models.AutoField(primary_key=True)
    stn_code = models.CharField(max_length=300)
    sampling_date = models.CharField(max_length=300)
    state = models.CharField(max_length=300)
    location = models.CharField(max_length=300)
    agency = models.CharField(max_length=300)
    type = models.CharField(max_length=300)
    so2 = models.CharField(max_length=300)
    no2 = models.CharField(max_length=300)
    rspm = models.CharField(max_length=300)
    spm = models.CharField(max_length=300)
    location_monitoring_station = models.CharField(max_length=300)
    pm2_5 = models.CharField(max_length=300)
    date = models.CharField(max_length=300)


class LiveAirQuality(models.Model):
    city = models.CharField(max_length=100)
    aqi = models.FloatField()
    pm25 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    so2 = models.FloatField(null=True, blank=True)
    no2 = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    o3 = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100, default='WAQI')