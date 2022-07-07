from rest_framework.serializers import *
from apps.api.models import UGSSettings, Repairs


class SettingsSerializer(ModelSerializer):
    class Meta:
        model = UGSSettings
        fields = [
            "capacity",
            "volume_in",
            "volume_out"
        ]


class RepairsSerializer(ModelSerializer):
    class Meta:
        model = Repairs
        fields = [
            "name",
            "start_date",
            "end_date",
            "in_coeff",
            "out_coeff"
        ]
