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

FILEFOLDER = 'temp/'
FILENAME_FIRST = FILEFOLDER+'ShiptorData.xlsx'
FILERESULT = FILEFOLDER + 'RESULT.xlsx'


def home(request):
    template = 'base.html'
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if len(request.FILES) == 1 and 'input' in request.FILES.keys():
                logger.debug(f"обработка входного файла - {request.FILES['input']}")
                s = request.FILES['input']
                logger.debug(f"{s}, {type(s)}")
                packages = file_handle.get_packages_from_file(s.temporary_file_path())
                df = shiptor.get_packages(packages)
                pd.DataFrame(df).to_excel(FILENAME_FIRST, header=True, index=False)
                return FileResponse(open(FILENAME_FIRST, 'rb'), as_attachment=True,
                                    filename="1 ShiptorData.xlsx")
            elif len(request.FILES) == 4: #сменить на 4
                request.FILES['input'] = FILENAME_FIRST
                result = file_handle.get_files_data(request.FILES)
                pd.DataFrame(result).to_excel(FILERESULT, header=True, index=False)
                return FileResponse(open(FILERESULT, 'rb'), as_attachment=True,
                                    filename="RESULT.xlsx")
            else:
                # Если функция не увидела файлов \ Если количество файлов != 4,1
                logger.error(f"request.FILES error", request.FILES, request.POST)
    else:
        form = UploadFileForm()
    return render(request, template, {'form': form})
