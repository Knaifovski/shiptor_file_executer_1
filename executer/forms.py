from django import forms
from django.db.models.fields.files import FieldFile


class UploadFileForm(forms.Form):
    input = forms.FileField(required=False, label="input" )
    om = forms.FileField(required=False, label="OM")
    vp = forms.FileField(required=False, label="ВП")
    vvp = forms.FileField(required=False, label="ВВП")


# class UploadFileForm(forms.Form):
#     title = forms.CharField(max_length=50)
#     file = forms.FileField()