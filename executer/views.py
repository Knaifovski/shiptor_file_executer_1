from django.http import FileResponse
from django.shortcuts import render
from loguru import logger
import pandas as pd
from pandas import ExcelWriter

from databases.databases import Standby_Shiptor_database
from core import config
from executer import file_handle
from executer.forms import UploadFileForm

# Create your views here.

settings = config.Settings()
shiptor = Standby_Shiptor_database(host= settings.shiptor_standby_base_host,
                                        database='shiptor',
                                        user=settings.user,
                                        password=settings.password)




def home(request):
    template = 'base.html'
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            request.FILES['input'] = settings.FILENAME_FIRST
            result = file_handle.get_files_data({'input': settings.FILENAME_FIRST,
                                                 'extradata': settings.FILENAME_SECOND})
            logger.debug(result)
            with ExcelWriter(settings.FILERESULT) as writer:
                result['simple'].to_excel(writer, sheet_name='Результат', header=True, index=False)
                result['result'].to_excel(writer, sheet_name='Подробнее', header=True, index=False)
                for sheet in result['extradata_dfs']:
                    result['extradata_dfs'][sheet].to_excel(writer, sheet_name=sheet)
            return FileResponse(open(settings.FILERESULT, 'rb'), as_attachment=True,
                                filename="RESULT.xlsx")
    else:
        form = UploadFileForm()
    return render(request, template, {'form': form, 'warehouses': settings.SAP_WAREHOUSES})
