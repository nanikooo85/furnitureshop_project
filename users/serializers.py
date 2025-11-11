# users/serializers.py - სრულიად სწორი შიგთავსი

from rest_framework import serializers
from .models import CustomUser

# ----------------------------------------------------
# CustomUser-ის სერიალიზატორი (რეგისტრაციისთვის)
# ----------------------------------------------------
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'password', 'first_name',
            'last_name', 'phone', 'address', 'birth_date'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate(self, data):
        if len(data['password']) < 6:
            raise serializers.ValidationError({"password": "Password must be at least 6 characters long."})
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
            birth_date=validated_data.get('birth_date', None)
        )
        return user