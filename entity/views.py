from django.shortcuts import render, redirect
from django.http import HttpResponse

import csv, StringIO, os, re, shutil

# Create your views here.

def index(request):
    path = os.path.dirname(os.path.abspath(__file__))
    
    # if userid, then "login" by loading projects
    userid = ""
    projects = []
    proj = ""
    if 'userid' in request.POST:
        userid = request.POST['userid']
        userpath = path + "/projects/" + userid

        # if html, then create a new project from html
        if 'html' in request.POST:
            html = request.POST['html']
            proj = html[0:-5]
            userpath = path + "/projects/" + userid + "/"
            src = path + "/html/" + request.POST['html']
            dst = userpath + request.POST['html']
            shutil.copyfile(src, dst)

            csvfile = proj + ".csv"
            with open(userpath + csvfile, "w+") as f:
                f.write("general,specific\n")

        # create current project list
        files = os.listdir(userpath)
        projects = []
        for f in files:
            if f.endswith(".html"):
                projects.append(f[0:-5])

    project_html = os.listdir(path + "/html/")

    # read current project name, if created this turn
    if proj == "" and 'proj' in request.POST:
        proj = request.POST['proj']
        
    return render(request, 'entity/index.html', 
                  {'userid': userid, 'projects': projects,
                   'proj': proj, 'project_html': project_html})

def annotated(request):
    path = os.path.dirname(os.path.abspath(__file__))
    
    # store the posted file as a global html file, if any
    if 'html' in request.FILES:
        content = request.FILES['html'].read()
        html = request.FILES['html'].name
        f = open(path + html, 'w+')
        f.write(content)
        f.close()
        response = HttpResponse(content_type='text/html')
        response.write(content)
        return response

    # if userid, then set path to user's project folder
    if not 'userid' in request.GET:
        return render(request, 'entity/annotated.html')    
    
    userid = request.GET['userid']

    # check the userid is alphanumeric for security
    if not re.match('^[\w]+$', userid):
        response = HttpResponse()
        response.status_code = 500
        response.reason_phrase = 'Userid must be alphanumeric.'
        return response

    # define the user's project path
    path = path + "/projects/" + userid + "/"

    # check if this is a request to load the file
    if 'proj' in request.GET and request.GET['proj'] != "":
        html = request.GET['proj'] + ".html"

        if html == ".html":
            return render(request, 'entity/annotated.html')  
        elif os.path.isfile(path + html):
            response = HttpResponse(content_type='text/html')
            with open(path + html, 'r') as f:
                content = f.read()
                response.write(content)
                return response
        else:
            return HttpResponse("Request not found: " + html)

    # else, check if this is a request to save the file
    elif 'proj' in request.POST and request.POST['proj'] != "":
        html = request.POST['proj'] + ".html"
        html_content = request.POST['annotated']

        with open(path + html, 'w+') as f:
            f.write(html_content)
        return HttpResponse("Request posted: " + html)

    return render(request, 'entity/annotated.html')    

def ontology(request):
    path = os.path.dirname(os.path.abspath(__file__))
    items = []

    # if userid, then set path to user's project folder
    if not 'userid' in request.GET:
        return render(request, 'entity/ontology.html', {'items': []});
    
    userid = request.GET['userid']

    # check the userid is alphanumeric for security
    if not re.match('^[\w]+$', userid):
        response = HttpResponse()
        response.status_code = 500
        response.reason_phrase = 'Userid must be alphanumeric.'
        return response

    # define the user's project path
    path = path + "/projects/" + userid + "/"

    # store the posted ontology file, if any
    if 'ontology' in request.FILES:
        content = request.FILES['ontology'].read()
        csvfile = request.POST['proj'] + ".csv"

        with open(path + csvfile, 'w+') as csvf:
            csvf.write(content)
            
        dialect = csv.Sniffer().sniff(content)
        stream = StringIO.StringIO(content)
        reader = csv.reader(stream, delimiter=',', dialect=dialect)
        
        # skip the header row, first
        reader.next()
        for row in reader:
            items.append(row)

    # check if this is a request to load the file
    elif 'proj' in request.GET and request.GET['proj'] != "":
        csvfile = request.GET['proj'] + ".csv"
        
        if os.path.isfile(path + csvfile):
            with open(path + csvfile, 'r') as csvf:
                content = csvf.read()
            
            dialect = csv.Sniffer().sniff(content)
            stream = StringIO.StringIO(content)
            reader = csv.reader(stream, delimiter=',', dialect=dialect)
        
            # skip the header row, first
            reader.next()
            for row in reader:
                print row
                items.append(row)

    # else, check if this is a request to save the file
    elif 'proj' in request.POST and request.POST['proj'] != "":
        csvfile = request.POST['proj'] + ".csv"
        items = request.POST['ontology'].split(";")
        
        with open(path + csvfile, 'w+') as csvf:
            writer = csv.writer(csvf)
            header = ["general", "specific"]
            writer.writerow(header)

            # write the file rows to the response
            for item in items:
                if len(item) == 0:
                    continue
                row = item.split(",")
                writer.writerow(row)
        return HttpResponse("Request posted: " + csvfile)

    return render(request, 'entity/ontology.html', {'items': items});
    
def download(request):
    path = os.path.dirname(os.path.abspath(__file__))
    userid = request.GET['userid']
    userpath = path + "/projects/" + userid + "/"
    filename = request.POST['file']

    # create the response header for the file download
    f = open(userpath + filename, 'r')
    content = f.read()
    f.close()
    response = HttpResponse(content)

    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    if filename.endswith(".csv"):
        response.content_type = 'text/csv';
    else:
        response.content_type = 'text/html';
    return response

