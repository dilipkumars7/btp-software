from btporders.models import MasterData, CacheData
from rest_framework import serializers

class MasterDataDbSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterData
        fields = '__all__'

class CacheDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CacheData
        fields = '__all__'