from django.shortcuts import render
from django.http import HttpResponse
from . import plots
from . import processdata

def index(request):
    data = processdata.Covid_data()
    activos = data.activeCasesIncrement()
    example_plot = plots.total_cases_map()
    return render(
        request,
        'dashboard/index.html',
        {
            'example_plot': example_plot,
            'activos': activos
        }
    )
# Create your views here.
