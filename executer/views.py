from django.http import FileResponse
from django.shortcuts import render
from loguru import logger
import pandas as pd


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
            if len(request.FILES) > 0:
                request.FILES['input'] = settings.FILENAME_FIRST
                result = file_handle.get_files_data(request.FILES)
                pd.DataFrame(result).to_excel(settings.FILERESULT, header=True, index=False)
                return FileResponse(open(settings.FILERESULT, 'rb'), as_attachment=True,
                                    filename="RESULT.xlsx")
            else:
                # Если функция не увидела файлов \ Если количество файлов != 4,1
                logger.error(f"request.FILES error files count = {len(request.FILES)}", request.FILES, request.POST)
    else:
        form = UploadFileForm()
    return render(request, template, {'form': form, 'warehouses': settings.SAP_WAREHOUSES})
