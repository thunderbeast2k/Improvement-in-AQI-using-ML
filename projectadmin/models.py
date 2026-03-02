from django.db import models

# Create your models here.
class DatatrainModel(models.Model):
    img=models.FileField()
    air_quality=models.CharField(max_length=100)
    predictionvalue=models.CharField(max_length=100)

class CheckWeatherModel(models.Model):
    usid=models.CharField(max_length=500)
    img_id=models.ForeignKey(DatatrainModel,on_delete=models.CASCADE,)
    img_path=models.CharField(max_length=500)
    rslt=models.CharField(max_length=500)