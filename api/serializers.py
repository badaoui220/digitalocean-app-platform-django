from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Paie, Consultant, Log
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class PaieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paie
        fields = ['id', 'mois', 'fichier', 'author', 'structure']


class ConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = ['id', 'nom', 'prenom', 'email', 'type']

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'name', 'email', 'structure', 'mois']
