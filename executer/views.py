from django.shortcuts import render

from databases.databases import Standby_Shiptor_database
from core import config
# Create your views here.

settings = config.Settings()
shiptor = Standby_Shiptor_database(host= settings.shiptor_standby_base_host,
                                        database='shiptor',
                                        user=settings.user,
                                        password=settings.password)

def home(request):
    template = 'base.html'
    packages = ["123570100000986978","123570100002480375","123570100002492765","123570100002642023","RP495127126",
                "RP503994757","RP505866284","RP506929421","RP508099830","SBC0005416826"]
    print(shiptor.get_packages(packages))
    return render(request, template)