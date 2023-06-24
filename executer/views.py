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
FILENAME_FIRST = FILEFOLDER+'1 ShiptorData.xlsx'


def home(request):
    template = 'base.html'
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if len(request.FILES) == 1 and 'input' in request.FILES.keys():
                logger.debug(f"обработка входного файла - {request.FILES['input']}")
                s = request.FILES['input']
                logger.debug(f"{s}, {type(s)}")
                packages = file_handle.get_data_from_file(s.temporary_file_path())
                df = shiptor.get_packages(packages)
                pd.DataFrame(df).to_excel(FILENAME_FIRST, header=True, index=False)
                return FileResponse(open(FILENAME_FIRST, 'rb'), as_attachment=True,
                                    filename="1 ShiptorData.xlsx")
            elif len(request.FILES) in (1,2,3,4): #сменить на 4
                # files = []
                # for file in request.FILES:
                #     files.append({'name': file, 'path': file.temporary_file_path()})
                request.FILES['input'] = FILENAME_FIRST
                # file_handle.get_files_data(request.FILES)
                file_handle.get_files_data(request.FILES)
            else:
                # Если функция не увидела файлов \ Если количество файлов != 4,1
                logger.error(f"request.FILES error", request.FILES, request.POST)
    else:
        form = UploadFileForm()
    # packages = ["123570100000986978","123570100002480375","123570100002492765","123570100002642023","RP495127126",
    #             "RP503994757","RP505866284","RP506929421","RP508099830","SBC0005416826"]
    # print(shiptor.get_packages(packages))


    # if request.method == "POST":
    #     form = UploadFileForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         logger.debug(request.FILES)
    # else:
    #     form = UploadFileForm()
    return render(request, template, {'form': form})

def export_shiptor_data(request):
    return FileResponse(open(FILENAME_FIRST, 'rb'), as_attachment=True, filename="daiy_export.xlsx")