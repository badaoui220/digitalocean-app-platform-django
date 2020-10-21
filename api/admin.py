# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Paie, Consultant, Log


class PaieAdmin(admin.ModelAdmin):
    list_display = ('id', 'mois', 'fichier', 'author', 'structure', 'created_on')
    list_filter = ("author",)
    search_fields = ['mois']


class ConsultantAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'email', 'type', 'created_on')

class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'structure', 'mois', 'status', 'fdp', 'msg', 'created_on')


admin.site.register(Paie, PaieAdmin)
admin.site.register(Consultant, ConsultantAdmin)
admin.site.register(Log, LogAdmin)
