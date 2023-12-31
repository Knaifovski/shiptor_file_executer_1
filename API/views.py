from re import split

from loguru import logger
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd

from API.serializer import MergeSerializer
from core import config
from databases.databases import Standby_Shiptor_database
from executer import file_handle

settings = config.Settings()
shiptor = Standby_Shiptor_database(host=settings.shiptor_standby_base_host,
                                   database='shiptor',
                                   user=settings.user,
                                   password=settings.password)




class GetPackages(APIView):

    def post(self, *args, **kwargs):
        logger.debug(f" args={args}, kwargs={kwargs} data= {self.request.data}")
        values = split('; |, |\n', self.request.data['packages'])
        prefix = self.request.data['prefix']
        logger.debug(f"values len = {len(values)}")

        try:
            i = 0
            while (i < len(values)):
                values[i] = values[i].rstrip().lstrip()
                values[i] = values[i].rstrip(',')
                values[i] = values[i].strip('\'\"\n')
                logger.debug(f"i={i}|value = {values[i]} len={len(values[i])}")
                if len(values[i]) < 4:
                    values.remove(values[i])
                    i = i - 1
                i += 1
        except IndexError:
            logger.debug(f"End of values. Values len = {len(values)}")
        if len(values) < 1:
            return Response({'result': "Не переданы значения"}, status=status.HTTP_400_BAD_REQUEST)
        logger.debug(f"apiresult = {values}")
        shiptordata = shiptor.get_packages(values)
        #first checking
        shiptordata = file_handle.checking_first(data=shiptordata, request_warehouse=prefix)
        # remove duplicates
        shiptordata = [dict(t) for t in {tuple(d.items()) for d in shiptordata}]
        df = pd.DataFrame(shiptordata).drop_duplicates(subset=["value"], keep='first')
        df.to_excel(settings.FILENAME_FIRST, header=True, index=False)
        result = "".join([f"{i['result']}\n" for i in shiptordata])
        return Response({"result": str(result), 'count': {len(values)}}, status=status.HTTP_200_OK)

class MergeData(APIView):
    """Merge data by api from front-end"""
    def post(self, *args, **kwargs):
        logger.debug(f"args = {args} kwargs = {kwargs}, data={self.request.data}")
        serialzer = MergeSerializer(data=self.request.data)
        serialzer.is_valid()
        data = serialzer.validated_data
        logger.debug(f"serializer data = {data}")
        writer = pd.ExcelWriter(settings.FILENAME_SECOND)
        if 'vvp_status' in data.keys() and 'vvp' in data.keys():
            vvp_df = pd.DataFrame(data['vvp'], columns=data['vvp'].keys())
            vvp_status_df = pd.DataFrame(data['vvp_status'], columns=data['vvp_status'].keys())
            merged = vvp_df.merge(vvp_status_df, on='документ', how='left')
            merged.to_excel(writer, index=False, sheet_name="vvp")
            del data['vvp_status']
            del data['vvp']
        for key in data.keys():
            dfs = []
            if type(data[key]) == dict:
                dfs.append(pd.DataFrame(data[key], columns=data[key].keys()))
            _ = [A.to_excel(writer, index=False, sheet_name="{0}".format(key)) for i, A in enumerate(dfs)]
        writer.close()
        return Response({"result": data}, status=status.HTTP_200_OK)
