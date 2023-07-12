import json
from re import split

from django.contrib.auth import login
from loguru import logger
from rest_framework import viewsets, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from core import config
from databases.databases import Standby_Shiptor_database

settings = config.Settings()
shiptor = Standby_Shiptor_database(host= settings.shiptor_standby_base_host,
                                        database='shiptor',
                                        user=settings.user,
                                        password=settings.password)

class GetPackages(APIView):

    def post(self, *args, **kwargs):
        logger.debug(f" args={args}, kwargs={kwargs} data= {self.request.data}")
        # values = self.request.data['packages'].split('\n')
        values = split('; |, |\*|\n', self.request.data['packages'])
        logger.debug(f"apiresult = {values}")
        shiptordata = shiptor.get_packages(values)
        result = "".join([f"{i['value']} {i['comment']}\n" for i in shiptordata])
        return Response({"result": str(result)}, status=status.HTTP_200_OK)
