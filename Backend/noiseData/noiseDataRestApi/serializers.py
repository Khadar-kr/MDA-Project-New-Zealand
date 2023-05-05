from rest_framework import serializers
from .models import noisedata

class noiseDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = noisedata
        fields = ['row_id','lamax','laeq','lceq','lcpeak','description','number_of_events','year','month','day','hour','hour_of_year','lc_humidity','lc_dwptemp','lc_rad','lc_rainin','lc_winddir','lc_windspeed','lc_temp']
