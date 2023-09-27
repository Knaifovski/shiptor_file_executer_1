import datetime
import re

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
        if 'om' in attrs.keys():
            attrs['om'] = self.text_to_dict(attrs['om'], fields=['result', 'Номер отправления', 'Дата ОМ'], name="ОМ")
        if 'vp' in attrs.keys():
            attrs['vp'] = self.text_to_dict(attrs['vp'], fields=['result', 'ВП'], name="ВП")
        if 'vvp' in attrs.keys():
            attrs['vvp'] = self.text_to_dict(attrs['vvp'], fields=['result', 'документ'],
                                             name="ВВП")
        if 'vvp_status' in attrs.keys():
            attrs['vvp_status'] = self.text_to_dict(attrs['vvp_status'],
                                                    fields=['документ', 'дата разгрузки', 'складское действие'],
                                                    name="ВВП_статус")
        if 'smm' in attrs.keys():
            attrs['smm'] = self.text_to_dict(attrs['smm'], fields=['result', 'Обращение', 'Ответ СММ'], name="СММ")
        logger.debug(f"Attrs keys: {attrs.keys()}")
        return attrs

    def text_to_dict(self, data: str, fields:list = None, name=None):
        data = data.split("\n")
        result = {field: [] for field in fields}
        logger.debug(f"data len={len(data)}, fields = {fields}")
        try:
            i = 0
            while (i < len(data)):
                # if line length < 4
                if len(data[i]) < 4:
                    data.remove(data[i])
                    continue
                delimiters = ["\t", r'\s{2,}']
                for delimiter in delimiters:
                    # line = ";".join(data[i].split(delimiter))
                    line = ";".join(re.split(delimiter, data[i]))
                line = line.split("\t")
                logger.debug(f"line = {line}, len = {len(line)}")
                if len(line) < len(fields):
                    for idx in range(len(fields)-len(line)):
                        line.append("Значение не передано")
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
        # if 'result' in result.keys():
        #     result = self.count(data=result, name=name)
        if name == 'ВВП':
            result = self.count_vvp(result)
        return result

    def count(self, data: dict, name=None):
        #
        # Deprecated
        #
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

    def count_vvp(self, data: dict, name="ВВП"):
        counter, counter_list = {}, []
        # add values to counter
        idx = 0
        for result in data['result']:
            if result in counter.keys():
                if data['документ'][idx] in counter[result].keys():
                    counter[result][data['документ'][idx]] += 1
                else:
                    counter[result][data['документ'][idx]] = 1
            else:
                counter[result] = {data['документ'][idx]: 1}
            idx += 1
        # add counter values to data
        idx = 0
        for result in data['result']:
            counter_list.append(len(counter[result].keys()))
            idx += 1
        data[f'кол-во {name}'] = counter_list
        return data
