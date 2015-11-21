from django.shortcuts import render, redirect
from django.http import HttpResponse

import csv, StringIO, os

# Create your views here.

def index(request):
    # read list of annotated files
    path = os.path.dirname(os.path.abspath(__file__)) + "/html/"
    files = os.listdir(path)

    return render(request, 'entity/index.html', 
                  {'files': files, 'html': ""})

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

def ontology(request):
    return render(request, 'entity/ontology.html', {'items': []});
    
def upload(request):
    path = os.path.dirname(os.path.abspath(__file__)) + "/html/"
    
    # read the ontology from a csv file, if any
    if 'ontology' in request.FILES:
        content = request.FILES['ontology'].read()
        dialect = csv.Sniffer().sniff(content)
        
        stream = StringIO.StringIO(content)
        reader = csv.reader(stream, delimiter=',', dialect=dialect)
        
        # skip the header row, first
        reader.next()
        items = []
        for row in reader:
            items.append(row)
        return render(request, 'entity/ontology.html', {'items': items})
            
    elif 'annotated' in request.FILES:
        content = request.FILES['annotated'].read()
        html = request.FILES['annotated'].name
        f = open(path + html, 'w')
        f.write(content)
        f.close()
        return redirect("annotated?html=" + html)

def download(request):
    if 'ontology' in request.POST:
        items = request.POST['ontology'].split(";")

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

    elif 'annotated' in request.POST:
        content = request.POST['annotated']
        print "OK"
        # create the response header for the file download
        response = HttpResponse(content, content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="annotated.html"'
    return response
