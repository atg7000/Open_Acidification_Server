from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from time_series.models import TimeSeries
from time_series.serializers import TimeSeriesSerializer
import math

@csrf_exempt
def time_series_list(request):
    # Return a list of all time series
    if request.method == 'GET':
        series = TimeSeries.objects.all()
        serializer = TimeSeriesSerializer(series, many=True)
        return JsonResponse(serializer.data, safe=False)

    # Save the provided time series
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = TimeSeriesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


def time_series_detail(request, id):
    # First, check if specified time series exists
    try:
        series = TimeSeries.objects.get(id=id)
    except TimeSeries.DoesNotExist:
        return HttpResponse(status=404)
    
    # Read the specified time series
    if request.method == 'GET':
        serializer = TimeSeriesSerializer(series)
        return JsonResponse(serializer.data)

    # Update the specified time series
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = TimeSeriesSerializer(series, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    # Delete the specified time series
    elif request.method == 'DELETE':
        series.delete()
        return HttpResponse(status=204)

@csrf_exempt
def time_series_generate_hold(request):
    # Return a time series representing the hold function of the specified parameters
    if request.method == 'GET':

        at = request.GET.get('at', default=8)

        return JsonResponse({'value': [float(at)], 'time': [0], 'interval': 0, 'description' : "Generated by hold function with value "+str(at)})

    # Save a time series representing the hold function of the specified parameters
    elif request.method == 'POST':

        at = request.POST.get('at', default=8)

        data = {'name': request.POST.get('name', default='Unnamed'), 'value': [float(at)], 'time': [0], 'interval': 0, 'notes' : "Generated by hold function with value "+str(at)}
        serializer = TimeSeriesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def time_series_generate_ramp(request):
    if request.method == 'GET':

        start = request.GET.get('start', default=7)
        end = request.GET.get('end', default=9)
        duration = request.GET.get('duration', default=600)
        
        return JsonResponse({'value': [float(start), float(end)], 'time': [0, int(duration)], 'interval': 0, 'description' : "Generated by ramp function with start value "+str(start)+", end value "+str(end)+", and duration "+str(duration)})
    
    elif request.method == 'POST':

        start = request.POST.get('start', default=7)
        end = request.POST.get('end', default=9)
        duration = request.POST.get('duration', default=600)

        data = {'name': request.POST.get('name', default='Unnamed'), 'value': [float(start), float(end)], 'time': [0, int(duration)], 'interval': 0, 'notes' : "Generated by ramp function with start value "+str(start)+", end value "+str(end)+", and duration "+str(duration)}
        serializer = TimeSeriesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def time_series_generate_sine(request):
    if request.method == 'GET':

        frequency = request.GET.get('frequency', default=600)
        amplitude = request.GET.get('amplitude', default=1)
        offset_x = request.GET.get('offset_x', default=0)
        offset_y = request.GET.get('offset_y', default=8)

        value = [round(point_in_wave((1/10) * i, 1, amplitude, offset_x, offset_y), 4) for i in range(0, 20)]
        time = [frequency/10 * i for i in range(0, 20)]

        return JsonResponse({'value': value, 'time': time, 'interval': frequency*2.1, 'description' : "Generated by sine function with frequency "+str(frequency)+", amplitude "+str(amplitude)+", offset_x "+str(offset_x)+", and offset_y "+str(offset_y)})

    elif request.method == 'POST':

        frequency = request.POST.get('frequency', default=600)
        amplitude = request.POST.get('amplitude', default=1)
        offset_x = request.POST.get('offset_x', default=0)
        offset_y = request.POST.get('offset_y', default=8)

        value = [round(point_in_wave((1/10) * i, 1, amplitude, offset_x, offset_y), 4) for i in range(0, 20)]
        time = [frequency/10 * i for i in range(0, 20)]

        data = {'name': request.POST.get('name', default='Unnamed'), 'value': value, 'time': time, 'interval': frequency*2.1, 'notes' : "Generated by sine function with frequency "+str(frequency)+", amplitude "+str(amplitude)+", offset_x "+str(offset_x)+", and offset_y "+str(offset_y)}
        serializer = TimeSeriesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

# Returns the specified point x in the wave of specified parameters
def point_in_wave(x, frequency, amplitude, offset_x, offset_y):
    return (math.sin((math.pi * x)/frequency + offset_x) * amplitude) + offset_y