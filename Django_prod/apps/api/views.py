# -*- encoding: utf-8 -*-
from deprecated import deprecated
"""
Copyright (c) 2019 - present AppSeed.us
"""
# Create your views here.
from apps.api.models import PointsIn, PointsOut, UGSNames, UGSSettings, Repairs
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from apps.api.serializers import SettingsSerializer, RepairsSerializer
from rest_framework import permissions, generics


@api_view(["GET", "POST"])
def ugs_charts(request, *args, **kwargs):
    if request.method == "GET":
        UGS_name = dict(request.GET)
        UGS_id = UGSNames.objects.filter(name=UGS_name["UGS"][0]).values("id").get()["id"]
        UGS_in = PointsIn.objects.filter(name_id=UGS_id)
        UGS_out = PointsOut.objects.filter(name_id=UGS_id)
        data = {}
        if UGS_out:
            data["Points_in"] = [{"x": data_UGS[0], "y":data_UGS[1]} for data_UGS in UGS_in.values_list("X", "Y")]
            data["Points_out"] = [{"x": data_UGS[0], "y":data_UGS[1]} for data_UGS in UGS_out.values_list("X", "Y")]
            data.update(SettingsSerializer(UGSSettings.objects.filter(name_id=UGS_id).first()).data)
        return Response(data)
    elif request.method == "POST":
        serializer = RepairsSerializer(request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


@deprecated(version='1.0.1', reason="You should use RepairsCreateListAPIView function to have GET and POST working")
@api_view(["GET", "POST"])
def repairs(request, *args, **kwargs):
    if request.method == "POST":
        serializer = RepairsSerializer(data=request.data, many=True)
        if serializer.is_valid():
            Repairs.objects.all().delete()
            serializer.save()
            return Response(serializer.validated_data, status=HTTP_201_CREATED)
    elif request.method == "GET":
        queryset = Repairs.objects.all()
        serializer = RepairsSerializer(queryset, many=True)
        return Response(serializer.data)

    return Response(status=HTTP_400_BAD_REQUEST)


class RepairsCreateListAPIView(generics.ListCreateAPIView):
    queryset = Repairs.objects.all()
    serializer_class = RepairsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.queryset.delete()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


repairs_create_api_view = RepairsCreateListAPIView.as_view()
