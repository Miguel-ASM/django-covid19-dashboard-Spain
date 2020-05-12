from django.shortcuts import render
from django.http import HttpResponse
from . import plotlytest

def index(request):
    example_plot = plotlytest.plot_somethin()
    return render(request,'dashboard/index.html',{'example_plot':example_plot})
# Create your views here.
