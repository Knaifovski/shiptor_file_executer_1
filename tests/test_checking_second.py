import pytest
import pandas as pd

from executer import file_handle


class TestCase_1:
    data = {
    'value': {0: 'TEST_CASE_1'},
    'id': {0: 556193482},
    'external_id': {0: 586921800000004555},
    'surrogate': {0: pd.NA},
    'main': {0: 586921800000004555},
    'method_id': {0: 482},
    'method': {0: 'Сберкурьер'},
    'shiptor_status': {0: 'return_to_sender'},
    'delivered_at': {0: pd.NA},
    'returned_at': {0: pd.Timestamp('2023-03-01 01:02:49')},
    'return_id': {0: pd.NA},
    'reception_warehouse_id': {0: pd.NA},
    'project_id': {0: 101849},
    'project': {0: 'Marketplace (ФК)'},
    'previous_id': {0: pd.NA},
    'warehouse_name': {0: 'Хабаровск'},
    'comment': {0: pd.NA},
    'request_warehouse': {0: 12357},
    'result': {0: '586921800000004555'},
    'SAP_WH': {0: 8000},
    'Номер отправления': {0: pd.NA},
    'Дата ОМ': {0: pd.NA}
    }

    def test_external_id(self):
        assert file_handle.check_problem(self.data, i=0) == None

    def test_check_merchant(self):
        assert file_handle.check_merchant(self.data, i=0) == None

    def test_check_warehouse_prefix_not_equal(self):
        assert file_handle.check_warehouse_prefix_not_equal(self.data, i=0) != None

    def test_check_status_delivered(self):
        assert file_handle.check_status_delivered(self.data, i=0) == f"[СКЛАД-НА ВОЗВРАТ] передать на сортировку"

    def test_check_status_returned(self):
        assert file_handle.check_status_returned(self.data, i=0) != None

    def test_check_iseasyreturn(self):
        assert file_handle.check_iseasyreturn(self.data, i=0) == None

    def test_check_project_is_not_smm(self):
        assert file_handle.check_project_is_not_smm(self.data, i=0) == None
    def test_check_vvp_ishave(self):
        assert file_handle.check_vvp_ishave(data=self.data, i=0, easyreturn=False) \
               == f"[СММ - ВВП ФФ] {self.data['external_id'][0]} - номер заказа (значения не переданы)"


class TestCase_with_VVP_uniq(TestCase_1):
    data = {
    'value': {0: 'TEST_CASE_1'},
    'id': {0: 556193482},
    'returned_at': {0: pd.Timestamp('2023-03-01 01:02:49')},
    'external_id': {0: 586921800000004555},
    'method_id': {0: 482},
    'shiptor_status': {0: 'return_to_sender'},
    'delivered_at': {0: pd.NA},
    'project_id': {0: 101849},
    'warehouse_name': {0: 'Хабаровск'},
    'comment': {0: pd.NA},
    'request_warehouse': {0: 12357},
    'result': {0: '586921800000004555'},
    'SAP_WH': {0: 8000},
    # VVP
    'кол-во ВВП': {0: '1'},
    'складское действие': {0: 'завершено'}, # 'завершено', 'завершено частично', else
    # OM
    'Номер отправления': {0: pd.NA},
    'Дата ОМ': {0: pd.NA}
    }


    def __init__(self):
        self.data = TestCase_with_VVP_uniq.data

    def test_check_vvp_ishave(self):
        assert file_handle.check_vvp_ishave(self.data, i=0) == "[СКЛАД] ВВП уже завершено"

class TestCase_with_VVP_notunique(TestCase_with_VVP_uniq):
    data = {
        'кол-во ВВП': {0: 2}
    }

    def test_check_vvp_is_have(self):
        assert file_handle.check_vvp_ishave(self.data, i=0) == "[SAP] Несколько ВВП - удалить дубль"



def checking(data: dict, idx = 0):
    i = idx
    comment = []
    for package in data['value']:
        if data['id'][i] is pd.NA or pd.isna(data['external_id'][i]):
            # посылка не создана в шипторе
            # SKRIPTDLYAOBRAB-32: Проверка. ОМ проведен
            comment.append("[SHIPTOR] Посылка не создана в shiptor")
            if 'Дата ОМ' in data.keys():
                if pd.isna(data['Дата ОМ'][i]):
                    comment.append("[СКЛАД] Проверить ОМ\некорректный ШК")
                else:
                    comment.append(file_handle.check_vvp_ishave(data, i))
        else:
            # посылка создана в шипторое
            is_not_smm = file_handle.check_project_is_not_smm(data, i)
            if is_not_smm:
                comment.append(is_not_smm)
            else:
                is_merchant = file_handle.check_merchant(data, i)
                easyreturn = file_handle.check_iseasyreturn(data, i)
                if easyreturn:
                    comment.append(file_handle.check_vvp_ishave(data, i, easyreturn=True))
                else:
                    wh_prefix_not_equal = file_handle.check_warehouse_prefix_not_equal(data, i)
                    # external_id пустой, название товара или RP
                    if wh_prefix_not_equal is None and len(str(data['external_id'][i])) != 18:
                        comment.append("[Ручной разбор]")
                    else:
                        status_check = file_handle.check_status_returned(data, i)
                        if status_check:
                            # comment.append(status_check) Не добавляем статус в коммент
                            if wh_prefix_not_equal:
                                comment.append(wh_prefix_not_equal)
                            else:
                                comment.append(file_handle.check_vvp_ishave(data, i))
                        else:
                            comment.append(file_handle.check_status_delivered(data, i))
    return ",".join(comment)

def data_generator(extradata: dict):
    data = {
    'value': {0: 'TEST_CASE_1'},
    'id': {0: 556193482},
    'returned_at': {0: pd.Timestamp('2023-03-01 01:02:49')},
    'external_id': {0: 586921800000004555},
    'method_id': {0: 482},
    'shiptor_status': {0: 'return_to_sender'},
    'delivered_at': {0: pd.NA},
    'project_id': {0: 101849},
    'warehouse_name': {0: 'ФФ Артем'},
    'comment': {0: pd.NA},
    'request_warehouse': {0: 58692},
    'result': {0: '586921800000004555'},
    'SAP_WH': {0: 58692},
    # VVP
    # 'кол-во ВВП': {0: '1'},
    # 'складское действие': {0: 'завершено'}, # 'завершено', 'завершено частично', else
    # OM
    # 'Номер отправления': {0: pd.NA},
    # 'Дата ОМ': {0: pd.NA}
    }
    for key, value in extradata.items():
        data[key] = {0: value}
    return data


def test_1():
    extradata = {'кол-во ВВП': '1', 'складское действие': 'завершено'}
    data = data_generator(extradata)
    assert checking(data) == '[СКЛАД] ВВП уже завершено'

def test_is_smm():
    extradata = {'project_id': 101}
    data = data_generator(extradata)
    assert checking(data) == '[СКЛАД] Не СММ'

def test_3():
    extrdata = {'external_id': "RP222111"}
    data = data_generator(extrdata)
    assert checking(data) == f"[APP] Не найдено склада SAP с значением {data['external_id'][0]}"
    extrdata = {'external_id': "CRCCS222111"}
    data = data_generator(extrdata)
    assert checking(data) == f"[APP] Не найдено склада SAP с значением {data['external_id'][0]}"
    # Легкий возврат
    extrdata = {'external_id': "R222111"}
    data = data_generator(extrdata)
    assert checking(data) == '[СММ - ВВП ЛВ] RP556193482-R222111'
    extrdata = {'external_id': "CCSR222111"}
    data = data_generator(extrdata)
    assert checking(data) == '[СММ - ВВП ЛВ] RP556193482-CCSR222111'

def test_4_easy_return():
    # ввп не уникально
    extrdata = {'external_id': "CCS1111", 'кол-во ВВП': 2}
    data = data_generator(extrdata)
    assert checking(data) == '[SAP] Несколько ВВП - удалить дубль'
    # ввп уникально
    extrdata = {'external_id': "CCS1111", 'кол-во ВВП': 1}
    data = data_generator(extrdata)
    assert checking(data) == 'ВВП уникально'
    # ввп не уникально, статус передан
    extrdata = {'external_id': "CCS1111", 'кол-во ВВП': 2, 'складское действие': 'завершено'}
    data = data_generator(extrdata)
    assert checking(data) == '[SAP] Несколько ВВП - удалить дубль'
    # ввп уникально, статус передан - завершено
    extrdata = {'external_id': "CCS1111", 'кол-во ВВП': 1, 'складское действие': 'завершено'}
    data = data_generator(extrdata)
    assert checking(data) == '[СКЛАД] ВВП уже завершено'
    # ввп уникально, статус передан - не завершено
    extrdata = {'external_id': "R111111", 'кол-во ВВП': 1, 'складское действие': 'не завершено'}
    data = data_generator(extrdata)
    assert checking(data) == '[СКЛАД] ВВП создано - проверьте актуальность'
    # ввп уникально, статус передан - другой
    extrdata = {'external_id': "R111111", 'кол-во ВВП': 1, 'складское действие': 'другой'}
    data = data_generator(extrdata)
    assert checking(data) == '[СКЛАД] ВВП создано - проверьте актуальность'

def test_5_not_found_in_shiptor():
    extrdata = {'id': pd.NA, 'кол-во ВВП': 1, 'складское действие': 'другой'}
    data = data_generator(extrdata)
    assert checking(data) == '[SHIPTOR] Посылка не создана в shiptor'
    # ом не проведено
    extrdata = {'id': pd.NA, 'Дата ОМ': pd.NA, 'складское действие': 'другой'}
    data = data_generator(extrdata)
    assert checking(data) == '[SHIPTOR] Посылка не создана в shiptor,[СКЛАД] Проверить ОМ\некорректный ШК'
    # ом не проведено
    extrdata = {'id': pd.NA, 'Дата ОМ': 1, 'кол-во ВВП': 1, 'складское действие': 'другой'}
    data = data_generator(extrdata)
    assert checking(data) == '[SHIPTOR] Посылка не создана в shiptor,[СКЛАД] ВВП создано - проверьте актуальность'

def test_6_left():
    # extradata = {'external_id': pd.NA}
    # data = data_generator(extradata)
    # assert checking(data) == 1

    #склад соответствует
    # ВВП НЕТ
    extradata = {'shiptor_status': 'return_to_sender'}
    data = data_generator(extradata)
    print(data)
    print(f"[СММ - ВВП ФФ] {data['external_id'][0]} + номер заказа (значения не переданы)")
    assert checking(data) == f"[СММ - ВВП ФФ] {data['external_id'][0]} - номер заказа (значения не переданы)"
    # ВВП НЕТ, есть ОМ
    extradata = {'shiptor_status': 'return_to_sender', 'Номер отправления': 1117}
    data = data_generator(extradata)
    assert checking(data) == f"[СММ - ВВП ФФ] {data['external_id'][0]}-1117"
    # ВВП ЕСТЬ УНИКАЛЬНО
    extradata = {'shiptor_status': 'return_to_sender', 'кол-во ВВП': 1}
    data = data_generator(extradata)
    assert checking(data) == f"ВВП уникально"
    # склад не соответствует
    extradata = {'shiptor_status': 'return_to_sender', 'request_warehouse': "9999999"}
    data = data_generator(extradata)
    assert checking(data).startswith(f"[СКЛАД] Засыл, передать")

    # Статус доставлено
    extradata = {'shiptor_status': 'delivered'}
    data = data_generator(extradata)
    assert checking(data) == f"[СКЛАД] Принять не системно"
    # Статус другой
    extradata = {'shiptor_status': 'sent'}
    data = data_generator(extradata)
    assert checking(data) == f"[СКЛАД-НА ВОЗВРАТ] передать на сортировку"