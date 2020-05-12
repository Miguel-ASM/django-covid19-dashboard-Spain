from django.shortcuts import render
from django.http import HttpResponse
from . import plots

def index(request):
    example_plot = plots.total_cases_map()
    return render(request,'dashboard/index.html',{'example_plot':example_plot})
# Create your views here.
