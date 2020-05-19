from django.shortcuts import render
from django.http import HttpResponse
from . import plots
from . import processdata

def index(request):
    data = processdata.Covid_data()
    statusReport = data.returnStatusReport()
    total_cases_map = plots.total_cases_map()
    national_growth_plot = plots.makeNationalGrowthPlot()
    return render(
        request,
        'dashboard/index.html',
        {
            'total_cases_map': total_cases_map,
            'national_growth_plot': national_growth_plot,
            'statusReport': statusReport
        }
    )
# Create your views here.
