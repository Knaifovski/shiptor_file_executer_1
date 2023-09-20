import datetime

from django.core.exceptions import ObjectDoesNotExist
from loguru import logger
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext as _


class MergeSerializer(serializers.Serializer):
    om = serializers.CharField(required=False)
    vvp = serializers.CharField(required=False)
    vvp_status = serializers.CharField(required=False)
    smm = serializers.CharField(required=False)

    def validate(self, attrs):
        logger.debug(f"attrs = {attrs} keys={attrs.keys()}")
        try:
            attrs['om'] = self.text_to_dict(attrs['om'], fields=['result', 'Номер отправления', 'Дата ОМ'], name="ОМ")
        except KeyError:
            pass
        try:
            attrs['vp'] = self.text_to_dict(attrs['vp'], fields=['result', 'ВП'], name="ВП")
        except KeyError:
            pass
        try:
            attrs['vvp'] = self.text_to_dict(attrs['vvp'], fields=['result', 'документ'],
                                             name="ВВП")
        except KeyError:
            pass
        try:
            attrs['vvp_status'] = self.text_to_dict(attrs['vvp_status'],
                                                    fields=['документ', 'дата разгрузки', 'складское действие'],
                                                    name="ВВП_статус")
        except KeyError:
            pass
        try:
            attrs['smm'] = self.text_to_dict(attrs['smm'], fields=['result', 'Обращение', 'Ответ СММ'], name="СММ")
        except KeyError:
            pass
        if 'vvp_status' in attrs.keys() and 'vvp' in attrs.keys():
            attrs['vvp'] = attrs['vvp'] | attrs['vvp_status']
            del attrs['vvp_status']
        logger.debug(f"Attrs keys: {attrs.keys()}")
        return attrs

    def text_to_dict(self, data: str, fields:list = None, name=None):
        data = data.split("\n")
        result = {field: [] for field in fields}
        logger.debug(f"data len={len(data)}")
        try:
            i = 0
            while (i < len(data)):
                # if line length < 4
                if len(data[i]) < 4:
                    data.remove(data[i])
                    continue
                delimiters = ["\n", "\t"]
                for delimiter in delimiters:
                    line = ";".join(data[i].split(delimiter))
                line = line.split(";")
                if len(line) == 1:
                    line = [data[i], "Да"]
                for key in fields:
                    for value in line:
                        result[key].append(value)
                        line.remove(value)
                        break
                i += 1
        except IndexError:
            logger.debug(f"End of values")
        except Exception as e:
            logger.error(f"Error {e}")
        logger.debug(f"Result = {result}")
        if 'external' in result.keys():
            result = self.count(data=result, name=name)
        return result

    def count(self, data: dict, name=None):
        counter, counter_list = {}, []
        # add values to counter
        for external in data['result']:
            if external in counter.keys():
                counter[external] += 1
            else:
                counter[external] = 1
        # add counter values to data
        for external in data['result']:
            counter_list.append(counter[external])
        data[f'кол-во {name}'] = counter_list
        logger.debug(f"{name} data: {data}")
        return data


