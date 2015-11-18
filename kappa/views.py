from django.shortcuts import render
from django.http import HttpResponse
from kappa import read_items, compute_response_table, compute_cohens, compute_fleiss, compute_vanbelle

import csv

# Create your views here.

def tutorial(request):
    return render(request, 'kappa/tutorial.html')

def kappa(request):
    return render(request, 'kappa/kappa.html')

def input(request):
    return render(request, 'kappa/input.html')

def newinput(request):
    items = request.POST['items']
    raters = request.POST['raters']

    if not items.isdigit() or not raters.isdigit():
        return render(request, 'kappa/input.html')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ratings.csv"'

    writer = csv.writer(response)
    header = [""]
    ratings = []
    for i in range(1, int(raters) + 1):
        header.append("Rater " + str(i))
        ratings.append("")

    writer.writerow(header)
    for i in range(1, int(items) + 1):
        row = [i]
        row.extend(ratings)
        writer.writerow(row)

    return response

def analyze(request):
    if request.method != 'POST':
        return redirect('index')
    
    datafile1 = request.FILES['datafile1'].read().splitlines()
    filename1 = request.FILES['datafile1'].name
    raters1, codes1, items1, coded_items1 = read_items(datafile1)

    if len(raters1) == 2:
        p_o, p_e, k = compute_cohens(raters1, coded_items1, codes1)
        ckappa1 = "{0:.3f}".format(round(k, 3))
    else:
        ckappa1 = "-1"
    p, p_e, k = compute_fleiss(coded_items1, codes1)
    fkappa1 = "{0:.3f}".format(round(k, 3))

    if 'datafile2' in request.FILES:
        datafile2 = request.FILES['datafile2'].read().splitlines()
        filename2 = request.FILES['datafile2'].name
        raters2, codes2, items2, coded_items2 = read_items(datafile2)

        if len(raters2) == 2:
            p_o, p_e, k = compute_cohens(raters2, coded_items2, codes2)
            ckappa2 = "{0:.3f}".format(round(k, 3))
        else:
            ckappa2 = "-1"
        p, p_e, k = compute_fleiss(coded_items2, codes2)
        fkappa2 = "{0:.3f}".format(round(k, 3))

        if len(items1) == len(items2):
            codes = list(set(codes1) | set(codes2))
            n1, p_ij1, p_j1 = compute_response_table(coded_items1, codes)
            n2, p_ij2, p_j2 = compute_response_table(coded_items2, codes)
            p_o, p_e, p_m, k = compute_vanbelle(n1, p_ij1, p_j1, p_ij2, p_j2)
            vkappa = "{0:.3f}".format(round(k, 3))
    else:
        filename2 = ""
        ckappa2 = "-1"
        fkappa2 = "-1"
        raters2 = []
        items2 = []
        codes2 = []
        vkappa = "-1"

    return render(request, 'kappa/result.html',{
            'filename1': filename1,
            'ckappa1': ckappa1,
            'fkappa1': fkappa1,
            'raters1': sorted(raters1),
            'items1': sorted(items1),
            'codes1': sorted(codes1),
            'filename2': filename2,
            'ckappa2': ckappa2,
            'fkappa2': fkappa2,
            'raters2': sorted(raters2),
            'items2': sorted(items2),
            'codes2': sorted(codes2),
            'vkappa': vkappa,
            })

    
