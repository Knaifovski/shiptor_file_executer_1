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
        logger.debug(f"sheet={extradata_dfs[sheet]}")
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

@log
def checking_first(data: list, request_warehouse=None):
    """Check packages from database data and add comments"""
    idx = 0
    for package in data:
        logger.info(f"Package = {package}")
        comment = []
        package['request_warehouse'] = request_warehouse
        package['SAP_WH'] = None
        if package['id'] is None:
            package['result'] = package['value']
            comment.append("Не найдено в Shiptor")
            continue

        # get sap warehouse id
        try:
            if package['external_id']:
                # easy return
                if not str(package['external_id']).startswith("RP") and (
                        str(package['external_id']).startswith(('R', "CCS"))):
                    comment.append("Easy Return")
                    package['result'] = f"RP{package['id']}"
                else:
                    package['result'] = package['external_id']
                package['SAP_WH'] = settings.SAP_WAREHOUSES[package['external_id'][0:5]]['sap_wh_id']
            else:
                package['SAP_WH'] = settings.SAP_WAREHOUSES[package['value'][0:5]]['sap_wh_id']
        except:
            package['SAP_WH'] = None

        if 'result' not in package.keys() or package['result'] is None:
            package['result'] = package['value']
        if len(comment) > 1:
            package['comment'] = ",".join(comment)
        idx += 1
        logger.debug(package)
    return data

@log
def checking_second(data: pd.DataFrame):
    data = data.to_dict()
    logger.debug(data)
    idx = 0 #index курсор
    for package in data['value']:
        comment = full_checking(data, idx)
        data['comment'][idx] = ",".join(comment)
        idx += 1
    return pd.DataFrame(data)

def full_checking(data: dict, idx):
    comment = []
    if data['id'][idx] is pd.NA or (not data['id'][idx] is pd.NA and pd.isna(data['external_id'][idx])):
        # посылка не создана в шипторе
        # SKRIPTDLYAOBRAB-32: Проверка. ОМ проведен
        # comment.append("[SHIPTOR] Посылка не создана в shiptor")
        if ('Дата ОМ' in data.keys() and pd.isna(data['Дата ОМ'][idx])) or 'Дата ОМ' not in data.keys():
            comment.append("[СКЛАД] Проверить ОМ\некорректный ШК")
        else:
            comment.append(check_vvp_ishave(data, idx))
    else:
        # посылка создана в шипторое
        is_multiplace = check_ismultiplace(data,idx)
        is_not_smm = check_project_is_not_smm(data, idx)
        if is_multiplace:
            comment.append(is_multiplace)
        if is_not_smm:
            comment.append(is_not_smm)
        if is_not_smm or is_multiplace:
            pass
        else:
            is_merchant = check_merchant(data, idx)
            # if is_merchant:
            #     comment.append(is_merchant)
            # is_has_problem = check_problem(data, idx)
            # if is_has_problem:
            #     comment.append(is_has_problem)
            easyreturn = check_iseasyreturn(data, idx)
            if easyreturn:
                comment.append(check_vvp_ishave(data, idx, easyreturn=True))
            else:
                wh_prefix_not_equal = check_warehouse_prefix_not_equal(data, idx)
                logger.debug(f"Количество символов external_id = {len(str(data['external_id'][idx]))}")
                logger.debug(f"префикс склада = {wh_prefix_not_equal}")
                logger.debug(f"Условие выполняется? {len(str(data['external_id'][idx])) == 18 and wh_prefix_not_equal == None}")
                if len(str(data['external_id'][idx])) == 18 and wh_prefix_not_equal == None:
                    is_returned = check_status_isreturned(data, idx)
                    if is_returned:
                        if wh_prefix_not_equal:
                            comment.append(wh_prefix_not_equal)
                        else:
                            comment.append(check_vvp_ishave(data, idx))
                    else:
                        comment.append(check_status_delivered(data, idx))
                else:
                    comment.append("[Ручной разбор] external")
    logger.debug(comment)
    return comment

@log
def check_ismultiplace(data: dict, i: int):
    comment = None
    if data['package_type'][i] == 'multiplace':
        comment = "[Многоместка] Ручной разбор"
    return comment

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
            logger.debug(f"{str(int(data['external_id'][i]))[0:5]}")
            warehouse_data = settings.SAP_WAREHOUSES[str(int(data['external_id'][i]))[0:5]]
            if data['request_warehouse'][i] != warehouse_data['prefix']:
                comment = f"[СКЛАД] Засыл, передать в {warehouse_data['shiptor_wh_name']}"
        except Exception as e:
            comment = f"[APP] Не найдено склада SAP с значением {data['external_id'][i]}"
    return comment

@log
def check_status_delivered(data, i):
    comment = None
    if data['shiptor_status'][i] in ('delivered'):
        comment = f"[СКЛАД] Принять не системно"
    else:
        comment = f"[СКЛАД-НЕ ВОЗВРАТ] передать на сортировку"
    return comment

@log
def check_status_isreturned(data, i):
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
def check_project_is_not_smm(data: dict, i: int):
    """Проверка. Проект СММ или нет"""
    comment = None
    if data['project_id'][i] not in (101849, 232708):
        comment = "[СКЛАД] Не СММ"
    return comment

@log
def check_vvp_ishave(data: dict, i: int, easyreturn=False):
    # SKRIPTDLYAOBRAB-33: Проверка. Есть ВВП
    comment = None
    # Если ВВП НЕТ
    if 'кол-во ВВП' not in data.keys() or pd.isna(data['кол-во ВВП'][i]):
        if easyreturn:
            comment = f"[СММ - ВВП ЛВ] RP{int(data['id'][i])}-{data['external_id'][i]}"
        else:
            if 'Номер отправления' in data.keys() and not pd.isna(data['Номер отправления'][i]):
                comment = f"[СММ - ВВП ФФ] {data['result'][i]}-{int(data['Номер отправления'][i])}"
            else:
                comment = f"[СММ - ВВП ФФ] {data['external_id'][i]} - номер заказа (значения не переданы)"
    # Если ВВП ЕСТЬ
    else:
        comment = check_vvp_unique(data, i)
    return comment

@log
def check_vvp_unique(data: dict, i: int):
    """Проверка уникальности ВВП"""
    # SKRIPTDLYAOBRAB-34: Проверка. ВВП уникально
    comment = None
    if not pd.isna(data['кол-во ВВП'][i]) and int(data['кол-во ВВП'][i]) != 1:
        comment = "[SAP] Несколько ВВП - удалить дубль"
    else:
        vvp_status = check_vvp_status(data, i)
        if vvp_status:
            comment = vvp_status
        else:
            comment = 'ВВП уникально'
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
