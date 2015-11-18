from django.shortcuts import render
from django.http import HttpResponse

import csv, StringIO, os

# Create your views here.

def index(request):
    items = []

    # read the ontology from a csv file, if any
    if 'upload' in request.FILES:
        content = request.FILES['upload'].read()
        dialect = csv.Sniffer().sniff(content)

        stream = StringIO.StringIO(content)
        reader = csv.reader(stream, delimiter=',', dialect=dialect)

        # skip the header row, first
        reader.next()
        for row in reader:
            items.append(row)

    # read list of annotated files
    path = os.path.dirname(os.path.abspath(__file__)) + "/html/"
    files = os.listdir(path)

    return render(request, 'entity/index.html', 
                  {'items': items, 'files': files})

def annotated(request):
    # read annotated file, if any
    path = os.path.dirname(os.path.abspath(__file__)) + "/html/"
    html = request.GET['html']

    if os.path.isfile(path + html):
        response = HttpResponse(content_type='text/html')
        with open(path + html, 'r') as f:
            content = f.read()
            response.write(content)
        return response
    else:
        return render(request, 'entity/annotated.html')

def download(request):
    items = request.POST['items'].split(";")

    # create the response header for the file download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ontology.csv"'

    # write the file header to response
    writer = csv.writer(response)
    header = ["general", "specific"]
    writer.writerow(header)

    # write the file rows to the response
    for item in items:
        if len(item) == 0:
            continue
        row = item.split(",")
        writer.writerow(row)

    return response
