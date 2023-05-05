from django.db import models

# Create your models here.
from django.db import models

class noisedata(models.Model):
    row_id = models.IntegerField()
    lamax = models.DecimalField(max_digits=50,decimal_places=25)
    laeq = models.DecimalField(max_digits=50,decimal_places=25)
    lceq = models.DecimalField(max_digits=50,decimal_places=25)
    lcpeak =models.DecimalField(max_digits=50,decimal_places=25)
    description = models.CharField(max_length=200)
    number_of_events = models.IntegerField()
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    # date = models.DateField()
    hour = models.TimeField()
    hour_of_year = models.IntegerField()
    lc_humidity =models.DecimalField(max_digits=50,decimal_places=25)
    lc_dwptemp =models.DecimalField(max_digits=50,decimal_places=25)
    lc_rad =models.DecimalField(max_digits=50,decimal_places=25)
    lc_rainin = models.DecimalField(max_digits=50,decimal_places=25)
    lc_winddir = models.DecimalField(max_digits=50,decimal_places=25)
    lc_windspeed = models.DecimalField(max_digits=50,decimal_places=25)
    lc_temp = models.DecimalField(max_digits=50,decimal_places=25)

class noiseLocation(models.Model):
    description = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    coordinates_longitude = models.CharField(max_length=400)
    coordinates_lattitude = models.CharField(max_length=400)
