# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext as _

from django.db import models
from django.contrib.auth.models import User


def upload_path(instance, filename):
    return '/'.join(['fdp', str(instance.mois), str(instance.structure), filename])

class Paie(models.Model):
    mois = models.CharField(max_length=32, blank=False, null=False)
    fichier = models.FileField(blank=True, null=True, upload_to=upload_path)
    author = models.CharField(max_length=32, blank=False, null=False)
    structure = models.CharField(max_length=32, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.mois


class Consultant(models.Model):
    STATUS = (
        ('WGT', _('Portage')),
        ('WG', _('CDI')),
        ('WGS', _('JEI')),
    )
    nom = models.CharField(max_length=50, blank=False, null=False)
    prenom = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=False, null=False)
    type = models.CharField(max_length=32, choices=STATUS, default='WGT')
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

def upload_path_fdp(instance, filename):
    return '/'.join(['fdp', str(instance.mois), str(instance.structure), str(instance.name), filename])

class Log(models.Model):
    STATUS = (
        ('OK', _('OK')),
        ('KO', _('KO')),
    )
    name  = models.CharField(max_length=50, blank=False, null=False)
    email = models.CharField(max_length=50, blank=False, null=False)
    structure = models.CharField(max_length=50, blank=False, null=False)
    mois = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=32, choices=STATUS, default='OK')
    fdp = models.FileField(blank=True, null=True, upload_to=upload_path_fdp)
    msg = models.TextField(blank=False, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)