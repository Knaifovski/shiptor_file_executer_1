import pytest
from API import serializer


def test_serializer_1():
    s = serializer.MergeSerializer()
    line = "1048678722		не начато"
    result = s.text_to_dict(data=line, fields=['документ', 'дата разгрузки', 'складское действие'])
    assert result['документ'] == ['1048678722']
    assert result['дата разгрузки'] == ['']
    assert result['складское действие'] == ["не начато"]
