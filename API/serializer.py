import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext as _
