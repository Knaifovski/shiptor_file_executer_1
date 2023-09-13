import datetime

from django.core.exceptions import ObjectDoesNotExist
from loguru import logger
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext as _


class MergeSerializer(serializers.Serializer):
    om = serializers.CharField(required=False)
    vvp = serializers.CharField(required=False)
    smm = serializers.CharField(required=False)

    def validate(self, attrs):
        logger.debug(f"attrs = {attrs} keys={attrs.keys()}")
        try:
            attrs['om'] = self.text_to_dict(attrs['om'], fields=['result', 'Номер отправления', 'Дата ОМ'])
        except KeyError:
            pass
        try:
            attrs['vp'] = self.text_to_dict(attrs['vp'], fields=['result', 'ВП'])
        except KeyError:
            pass
        try:
            attrs['vvp'] = self.text_to_dict(attrs['vvp'], fields=['result', 'дата разгрузки', 'складское действие'])
        except KeyError:
            pass
        try:
            attrs['smm'] = self.text_to_dict(attrs['smm'], fields=['result', 'Обращение', 'Ответ СММ'])
        except KeyError:
            pass
        return attrs


    def text_to_dict(self, data: str, fields:list = None):
        data = data.split("\n")
        result = {field: [] for field in fields}
        logger.debug(f"data len={len(data)}")
        try:
            i = 0
            while (i < len(data)):
                if len(data[i]) < 4:
                    data.remove(data[i])
                line = data[i].split("\t")
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
        return self.count(result)

    def count(self, data):
        counter = {}
        # add values to counter
        for line in data:
            if line['external'] in counter.keys():
                counter[line['external']] += 1
            else:
                counter[line['external']] = 1
        # add counter values to data
        for line in data:
            line['count'] = counter[line['external']]
        return data


