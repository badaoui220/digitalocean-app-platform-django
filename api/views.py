# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

# from django.shortcuts import render

# Create your views here.

from django.db.models import QuerySet

from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.response import Response


from django.core.mail import EmailMultiAlternatives


from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import UserSerializer, PaieSerializer, ConsultantSerializer, LogSerializer
from .models import Paie, Consultant, Log


from PyPDF2 import PdfFileWriter, PdfFileReader
import re, os
from django.conf import settings
from smtplib import SMTPException
import datetime



class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'id': token.user_id})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaieViewSet(viewsets.ModelViewSet):
    queryset = Paie.objects.all()
    serializer_class = PaieSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]



    def post(self, request, *args, **kwargs):
        fichier = request.data['fichier']
        mois = request.data['mois']
        author = request.data['author']
        structure = request.data['structure']

        Paie.objects.create(mois=mois, fichier=fichier, author=author, structure=structure)

        return HttpResponse({'message': 'Paie created'}, status=200)

class ConsultantViewSet(viewsets.ModelViewSet):
    queryset = Consultant.objects.all()
    serializer_class = ConsultantSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]


class ConsultantListBytype(ListAPIView):
    """Page detail view."""

    model = Consultant
    queryset = Consultant.objects.all()
    serializer_class = ConsultantSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        structure = self.kwargs['structure']
        return Consultant.objects.filter(type=structure).order_by('nom')

class LogView(ListModelMixin, CreateModelMixin, GenericAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, *kwargs)

    def post(self, request, *args, **kwargs):
        pdf_file = request.data.get('file')
        pdf_mois = request.data.get('mois')
        consultant_name="{} {}".format(request.data.get('nom'), request.data.get('prenom'))
        consultant_short_name = "{}.{}".format(request.data.get('prenom')[0].upper(),request.data.get('nom').replace(" ", "").upper())
        consultant_email=request.data.get('email')
        consultant_structure = request.data.get('structure')

        response_status = 200
        log_status = 'OK'
        response_message = 'Mail Sent'

        pdf_file_split = pdf_file.split('/')
        pdf_name = pdf_file_split[-1]

        inputpdf = PdfFileReader(open(settings.FDP_ROOT + "/" + pdf_mois + "/" + consultant_structure + "/" + pdf_name, "rb"))
        NumPages = inputpdf.getNumPages()

        pdf_writer = PdfFileWriter()
        output_filename = ""
        fileNameUpload = ""

        today = datetime.datetime.today()
        year = today.year
        month_list = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']
        month = month_list.index(pdf_mois)
        dateFormat = str(year) + '{:02d}'.format(month)

        for i in range(0, NumPages):
            PageObj = inputpdf.getPage(i)
            Text = PageObj.extractText()
            if re.search(consultant_name.lower(), Text.lower()):
                outPutFolder = settings.FDP_ROOT + "/" + pdf_mois + "/" + consultant_structure + "/" + consultant_short_name
                outPutFolderUpload = settings.FDP_URL + "/" + pdf_mois + "/" + consultant_structure + "/" + consultant_short_name
                pdf_writer.addPage(PageObj)
                if not os.path.exists(outPutFolder):
                    os.makedirs(outPutFolder)

                output_filename = '{}/bulletin_{}_{}.pdf'.format(outPutFolder, dateFormat, consultant_short_name)
                fileNameUpload = '{}/bulletin_{}_{}.pdf'.format(outPutFolderUpload, dateFormat, consultant_short_name)
                with open(output_filename,'wb') as out:
                    pdf_writer.write(out)

        if output_filename != "" and os.path.exists(output_filename):

            subject = "[{}] Fiche de Paie {} {}".format(consultant_structure, pdf_mois, year)
            email_from = "Service Paie {} <{}>".format(consultant_structure, settings.EMAIL_HOST_USER)
            recipient_list = [consultant_email,]
            text_content = 'Bonjour, Veuillez trouver ci-joint votre fiche de paie {} {}. PS1: Un expert URSSAF audite dorenavant les NDF, et nous avons du rembourser dans la limite imposee par celui ci. Si vous avez besoin de plus d elements, merci de contacter Elodie SOUFFLARD ou Hicham EL MANIARI. Cordialement. Ce mail a &eacute;t&eacute; gener&eacute; automatiquement, merci de ne pas r&eacute;pondre.'.format(pdf_mois, year)
            html_content = """\
                        <div>
                            Bonjour,<br /><br />
                            Veuillez trouver ci-joint votre fiche de paie {} {}.<br /><br />
                            PS1: Un expert URSSAF audite dorenavant les NDF, et nous avons du rembourser dans la limite imposee par celui ci. Si vous avez besoin de plus d elements, merci de contacter Elodie SOUFFLARD ou Hicham EL MANIARI.<br /><br />
                            Cordialement.<br /><br /><br />
                            Ce mail a &eacute;t&eacute; gener&eacute; automatiquement, merci de ne pas r&eacute;pondre.
                        </div>
                """.format(pdf_mois, year)
            fail_silently = False
            msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list, fail_silently)
            msg.attach_alternative(html_content, "text/html")
            msg.attach_file(output_filename)

            try:
                msg.send()
            except SMTPException as e:
                response_status = 400
                log_status = 'KO'
                response_message = 'Mail not sent : {}'.format(e)
        else:
            response_status = 400
            log_status = 'KO'
            response_message = 'Not exist on the main PDF'

        Log.objects.create(name=consultant_name, email=consultant_email, structure=consultant_structure, status=log_status, mois=pdf_mois, fdp=fileNameUpload, msg=response_message)
        return Response({'message': response_message}, status=response_status)