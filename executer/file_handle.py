import functools
from datetime import datetime

import pandas as pd
from django.utils.datastructures import MultiValueDict
from loguru import logger

from core.config import Settings

settings = Settings()

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f"Function {func.__name__} start")
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} success. Result = {result}")
            return result
        except Exception as e:
            logger.exception(f"Exception: {str(e)}")
            raise e
    return wrapper


def get_packages_from_file(file) -> list:
    """return list of dicts package data"""
    packages = []
    try:
        xl_file = pd.ExcelFile(file)
        dfs = {sheet_name: xl_file.parse(sheet_name) for sheet_name in xl_file.sheet_names}
        for df in dfs.values():
            packages = df['packages'].values.tolist()
        packages = [str(package) for package in packages]
        return packages
    except Exception as e:
        logger.error(f"UNEXPECTER ERROR: {e}")

def get_files_data(files: dict) -> dict:
    """Return dictionary with keys: result - merged data, extradata_dfs - extra sheets (om,vp,vvp,etc)
     result_simple - simple_sheet with minimal data"""
    PACKAGES_LIST: list
    input_file = files['input']
    logger.debug(f"Файл шиптора получен")
    extradata = pd.ExcelFile(files['extradata'])
    logger.debug(f"Файл с доп значениями прочитан")
    result = pd.read_excel(input_file, converters={'value': str, 'result': str})
    logger.debug(f"Файл шиптора прочитан")
    result.drop_duplicates(subset='result', inplace=True, ignore_index=True)
    logger.debug(f"Файл шиптора - дубликаты удалены")
    result.sort_values(by=['SAP_WH', 'project', 'method_id', 'comment'], inplace=True, ignore_index=True)
    logger.debug(f"Файл - шиптора удалены дубликаты")
    logger.debug(f"Создан массив для упрощенного отображения в отдельном листе")
    extradata_dfs = {sheet_name: extradata.parse(sheet_name) for sheet_name in extradata.sheet_names}
    logger.debug(f"Созданы фреймы из доп выгрузок")
    for sheet in extradata_dfs:
        logger.debug(f"sheet={sheet}")
        extradata_dfs[sheet]['result'] = extradata_dfs[sheet]['result'].astype(str)
        result = result.merge(extradata_dfs[sheet], on='result', how='left')
        logger.debug(f"{sheet} merge success")
        # add comments to data
    result.drop_duplicates(subset='result', inplace=True, ignore_index=True)
    result = checking_second(result)
    if 'документ' in result.columns:
        result_simple = result[['value', 'result', 'документ', 'SAP_WH', 'shiptor_status', 'returned_at',
                                'delivered_at', 'project', 'comment']].copy()
    else:
        result_simple = result[
            ['value', 'result', 'SAP_WH', 'shiptor_status', 'returned_at', 'delivered_at', 'project',
             'comment']].copy()

    result_simple.rename(columns={"value": "Изначальное значение", "result": "Значение для САП", "SAP_WH": "Склад САП",
                                  "shiptor_status": "Статус Шиптора", "returned_at": "Возвращено",
                                  "delivered_at": "Доставлено", "project": "Клиент",
                                  "comment": "Комментарий"}, errors='raise', inplace=True)

    return {'result': result, 'extradata_dfs': extradata_dfs, 'simple': result_simple}


def checking_first(data: list, request_warehouse=None):
    """Check packages from database data and add comments"""
    for package in data:
        comment = []
        package['request_warehouse'] = request_warehouse
        if package['id'] is None:
            package['result'] = package['value']
            comment.append("Не найдено в Shiptor")
            continue

        # get sap warehouse id
        try:
            if package['external_id']:
                package['SAP_WH'] = settings.SAP_WAREHOUSES[package['external_id'][0:5]]['sap_wh_id']
            else:
                package['SAP_WH'] = settings.SAP_WAREHOUSES[package['value'][0:5]]['sap_wh_id']
        except:
            package['SAP_WH'] = None

        #if external_id contain "*" then its merchant
        if str(package['external_id']).__contains__('*'):
            comment.append("Мерчант")

        if package['result'] is None:
            package['result'] = package['value']
            comment.append(package['comment']) #what its do?
        package['comment'] = ",".join(comment)
    return data

@log
def checking_second(data: pd.DataFrame):
    data = data.to_dict()
    i = 0 #index курсор
    for package in data['value']:
        # comment = str(data['comment'][i]).split(',')
        comment = []
        if data['id'][i] is pd.NA or pd.isna(data['external_id'][i]):
            # посылка не создана в шипторе
            #SKRIPTDLYAOBRAB-32: Проверка. ОМ проведен
            comment.append("[SHIPTOR] Посылка не создана в shiptor")
            if 'кол-во ОМ' not in data.keys() or data['кол-во ОМ'][i] == pd.NaT:
                comment.append("[СКЛАД] Проверить ОМ\некорректный ШК")
            else:
                comment.append(check_vvp_ishave(data, i))
        else:
            # посылка создана в шипторое
            is_smm = check_project_issmm(data, i)
            if is_smm:
                comment.append(is_smm)
                continue
            is_merchant = check_merchant(data, i)
            if is_merchant:
                comment.append(is_merchant)
            # is_has_problem = check_problem(data, i)
            # if is_has_problem:
            #     comment.append(is_has_problem)
            else:
                easyreturn = check_iseasyreturn(data, i)
                if easyreturn:
                    comment.append(check_vvp_ishave(data, i, easyreturn=True))
                else:
                    status_check = check_status_returned(data, i)
                    if status_check:
                        # comment.append(status_check) Не добавляем статус в коммент
                        wh_prefix_not_equal = check_warehouse_prefix_not_equal(data, i)
                        if wh_prefix_not_equal:
                            comment.append(wh_prefix_not_equal)
                        else:
                            comment.append(check_vvp_ishave(data, i))
                    else:
                        comment.append(check_status_delivered(data, i))
        print(comment)
        data['comment'][i] = ",".join(comment)
        i += 1
    return pd.DataFrame(data)

@log
def check_problem(data: dict, i: int):
    comment = None
    if data['method_id'][i] in (571, 827, 672):
        # Get Problem by date
        if data['delivered_at'][i]:
            if data['delivered_at'][i] > datetime(year=2023, month=6, day=16):
                comment = '[Проблема] СММ(SHPTRERP-4675)'
    else:
        if data['returned_at'][i] and data['returned_at'][i] > datetime(year=2023, month=6, day=16):
            comment = '[Проблема] СММ(SHPTRERP-4675)'
    return comment

@log
def check_merchant(data, i):
    comment = None
    if str(data['external_id'][i]).__contains__("*"):
        comment = 'Мерчант'
    return comment

@log
def check_warehouse_prefix_not_equal(data, i):
    comment = None
    if not pd.isna(data['SAP_WH'][i]) and not pd.isna(data['warehouse_name'][i]):
        try:
            warehouse_data = settings.SAP_WAREHOUSES[str(data['external_id'][i])[0:5]]
            if data['request_warehouse'][i] != warehouse_data['prefix']:
                comment = f"[СКЛАД] Засыл, передать в {warehouse_data['shiptor_wh_name']}"
        except KeyError as e:
            comment = f"[APP] Не найдено склада SAP с значением {e.args}"
    return comment

@log
def check_status_delivered(data, i):
    comment = None
    if data['shiptor_status'][i] in ('delivered'):
        comment = f"[СКЛАД] Принять не системно"
    else:
        comment = f"[СКЛАД-НА ВОЗВРАТ] передать на сортировку"
    return comment

@log
def check_status_returned(data, i):
    comment = None
    if data['shiptor_status'][i] in ('returned', 'return_to_sender'):
        comment = f"[СТАТУС] {data['shiptor_status'][i]}"
    return comment

@log
def check_iseasyreturn(data: dict, i: int):
    comment = None
    if (str(data['external_id'][i])[0:2] != "RP") and (str(data['external_id'][i]).startswith(('R', "CCS"))):
        comment = "Легкий возврат"
    return comment

@log
def check_project_issmm(data: dict, i: int):
    """Проверка. Проект СММ или нет"""
    comment = None
    if data['project_id'][i] not in (101849, 232708):
        comment = "[СКЛАД] Не СММ"
    return comment

@log
def check_vvp_ishave(data: dict, i: int, easyreturn=False):
    # SKRIPTDLYAOBRAB-33: Проверка. Есть ВВП
    comment = None
    if 'кол-во ВВП' not in data.keys() or data['кол-во ВВП'][i] == pd.NaT or pd.isna(data['кол-во ВВП'][i]):
        if easyreturn:
            comment = f"[СММ - ВВП ЛВ] RP{data['id'][i]}-{data['external_id'][i]}"
        else:
            if 'Номер отправления' in data.keys() and not pd.isna(data['Номер отправления'][i]):
                comment = f"[СММ - ВВП ФФ] {data['external_id'][i]}-{data['Номер отправления'][i]}"
            else:
                comment = "[СММ - ВВП ФФ] external_id + номер заказа"
    else:
        comment = check_vvp_unique(data, i)
    return comment

@log
def check_vvp_unique(data: dict, i: int):
    """Проверка уникальности ВВП"""
    # SKRIPTDLYAOBRAB-34: Проверка. ВВП уникально
    comment = None
    if not pd.isna(data['кол-во ВВП'][i]) and data['кол-во ВВП'][i] != 1:
        comment = "[SAP] Несколько ВВП - удалить дубль"
    else:
        comment = check_vvp_status(data, i)
    return comment

@log
def check_vvp_status(data: dict, i: int):
    """Проверка складского действия"""
    # SKRIPTDLYAOBRAB-26: Проверка. Статус ВВП
    comment = None
    if 'складское действие' in data.keys():
        if str(data['складское действие'][i]).lower() in ('завершено', 'завершено частично'):
            comment = "[СКЛАД] ВВП уже завершено"
        else:
            comment = "[СКЛАД] ВВП создано - проверьте актуальность"
    return comment
