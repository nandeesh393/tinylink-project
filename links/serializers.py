# links/serializers.py
from rest_framework import serializers
from .models import Link
import re

CODE_REGEX = re.compile(r'^[A-Za-z0-9]{6,8}$')

class LinkSerializer(serializers.ModelSerializer):
    target = serializers.URLField(source='target_url')

    class Meta:
        model = Link
        fields = ['code', 'target', 'clicks', 'created_at', 'last_clicked']

class LinkCreateSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    target = serializers.URLField()

    def validate_code(self, value):
        if not value:
            return value
        if not CODE_REGEX.match(value):
            raise serializers.ValidationError("code must match /^[A-Za-z0-9]{6,8}$/")
        return value
