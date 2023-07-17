from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    secret_key: str
    user: str
    password: str
    shiptor_standby_base_host: str
    FILEFOLDER = 'temp/'
    FILENAME_FIRST = FILEFOLDER + 'ShiptorData.xlsx'
    FILENAME_SECOND = FILEFOLDER + 'MergeData.xlsx'
    FILERESULT = FILEFOLDER + 'RESULT.xlsx'
    SAP_WAREHOUSES = {
        '12357': {'sap_wh_id': 1000, 'prefix': 12357, 'shiptor_wh_name': "Склад ФФ Москва Шарапово"},
        '58688': {'sap_wh_id': 1002, 'prefix': 58688, 'shiptor_wh_name': "Склад ФФ Воронеж-2"},
        '54858': {'sap_wh_id': 1003, 'prefix': 54858, 'shiptor_wh_name': "Склад ФФ Пушкино"},
        '60428': {'sap_wh_id': 1004, 'prefix': 60428, 'shiptor_wh_name': "Пушкино Холодная полка"},
        '58700': {'sap_wh_id': 2000, 'prefix': 58700, 'shiptor_wh_name': "Санкт-Петербург ФФ"},
        '60375': {'sap_wh_id': 2001, 'prefix': 60375, 'shiptor_wh_name': "Санкт-Петербург FMCGG"},
        '82334': {'sap_wh_id': 2002, 'prefix': 82334, 'shiptor_wh_name': "Склад ФФ Санкт-Петербург-2"},
        '74559': {'sap_wh_id': 3000, 'prefix': 74559,
                  'shiptor_wh_name': "Краснодар, fresh 2p, процесс СММ Холодная полка"},
        '58703': {'sap_wh_id': 3002, 'prefix': 58703, 'shiptor_wh_name': "Склад ФФ Волгоград"},
        '58709': {'sap_wh_id': 3003, 'prefix': 58709, 'shiptor_wh_name': "Склад ФФ Ростов-на-Дону"},
        '58690': {'sap_wh_id': 3004, 'prefix': 58690, 'shiptor_wh_name': "Склад ФФ Краснодар-2"},
        '58704': {'sap_wh_id': 5000, 'prefix': 58704, 'shiptor_wh_name': "Склад ФФ Уфа"},
        '58695': {'sap_wh_id': 5001, 'prefix': 58695, 'shiptor_wh_name': "Склад ФФ Самара"},
        '58710': {'sap_wh_id': 5002, 'prefix': 58710, 'shiptor_wh_name': "Склад ФФ Пермь"},
        '58698': {'sap_wh_id': 5003, 'prefix': 58698, 'shiptor_wh_name': "Нижний Новгород"},
        '58682': {'sap_wh_id': 5004, 'prefix': 58682, 'shiptor_wh_name': "Склад FMCG процесс СММ Самара-2"},
        '74557': {'sap_wh_id': 5005, 'prefix': 74557,
                  'shiptor_wh_name': "NNOV-2 - Холодная полка склада ФФ СММ в Нижнем Новгороде"},
        '58693': {'sap_wh_id': 6000, 'prefix': 58693, 'shiptor_wh_name': "Склад ФФ Екатеринбург"},
        '58707': {'sap_wh_id': 6001, 'prefix': 58707, 'shiptor_wh_name': "Склад ФФ Челябинск"},
        '60376': {'sap_wh_id': 7000, 'prefix': 60376, 'shiptor_wh_name': "Склад FMCG процесс СММ Новосибирск"},
        '58684': {'sap_wh_id': 7001, 'prefix': 58684, 'shiptor_wh_name': "Склад ФФ Новосибирск-2"},
        '58689': {'sap_wh_id': 7002, 'prefix': 58689, 'shiptor_wh_name': "Красноярск"},
        '58696': {'sap_wh_id': 7003, 'prefix': 58696, 'shiptor_wh_name': "Омск"},
        '58692': {'sap_wh_id': 8000, 'prefix': 58692, 'shiptor_wh_name': "Склад ФФ Артем "},
        '58702': {'sap_wh_id': 8001, 'prefix': 58702, 'shiptor_wh_name': "Хабаровск"}
    }
    class Config:
        env_file = os.path.join(os.getcwd(), '.env')
