from django.shortcuts import render

# Create your views here.
# myapp/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import noisedata
from .models import noiseLocation
from .serializers import noiseDataSerializer
from .serializers import noiseLocationSerializer

@api_view(['GET', 'POST'])
def noiseData_list(request):
    if request.method == 'GET':
        noise = noisedata.objects.all()
        serializer = noiseDataSerializer(noise, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = noiseDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def noise_detail(request, pk):
    try:
        noise = noisedata.objects.get(pk=pk)
    except noisedata.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = noiseDataSerializer(noise)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = noiseDataSerializer(noise, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        noise.delete()
        return Response(status=204)
    

@api_view(['GET', 'POST'])
def noiselocations_list(request):
    if request.method == 'GET':
        locations = noiseLocation.objects.all()
        serializer = noiseLocationSerializer(locations, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = noiseLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def noiselocations_detail(request, pk):
    try:
        locations = noiseLocation.objects.get(pk=pk)
    except noiseLocation.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = noiseLocationSerializer(locations)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = noiseLocationSerializer(locations, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        locations.delete()
        return Response(status=204)