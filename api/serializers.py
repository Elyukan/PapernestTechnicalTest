from rest_framework import serializers


class AddressSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)


class NetworkCoverageSerializer(serializers.Serializer):
    addresses = AddressSerializer(many=True)