from rest_framework import serializers
from .models import CarbonDataRow

class CarbonDataRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonDataRow
        fields = '__all__'