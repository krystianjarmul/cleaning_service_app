from rest_framework import serializers


class EmployeeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField(max_length=2)


class CustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    company_name = serializers.CharField(allow_blank=True, allow_null=True)
