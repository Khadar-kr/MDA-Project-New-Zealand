from django.shortcuts import render

# Create your views here.
# myapp/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import noisedata
from .serializers import noiseDataSerializer

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