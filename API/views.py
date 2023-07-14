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
import pandas as pd

from core import config
from databases.databases import Standby_Shiptor_database

settings = config.Settings()
shiptor = Standby_Shiptor_database(host=settings.shiptor_standby_base_host,
                                   database='shiptor',
                                   user=settings.user,
                                   password=settings.password)




class GetPackages(APIView):

    def post(self, *args, **kwargs):
        logger.debug(f" args={args}, kwargs={kwargs} data= {self.request.data}")
        values = split('; |, |\n', self.request.data['packages'])
        try:
            i = 0
            while (i < len(values)):
                values[i] = values[i].rstrip().lstrip()
                values[i] = values[i].rstrip(',')
                values[i] = values[i].strip('\'\"\n')
                logger.debug(f"i={i}|value = {values[i]} len={len(values[i])}")
                if len(values[i]) < 8:
                    values.remove(values[i])
                    i = i - 1
                i += 1

        except IndexError:
            logger.debug(f"End of values. Values len = {len(values)}")
        logger.debug(f"apiresult = {values}")
        shiptordata = shiptor.get_packages(values)
        df = pd.DataFrame(shiptordata).drop_duplicates(subset=["value"], keep='first')
        df.to_excel(settings.FILENAME_FIRST, header=True, index=False)
        result = "".join([f"{i['value']} {i['comment']}\n" for i in shiptordata])
        return Response({"result": str(result)}, status=status.HTTP_200_OK)
