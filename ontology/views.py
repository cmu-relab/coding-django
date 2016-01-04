from django.shortcuts import render,redirect
from django.http import HttpResponse

import jnius_config, os.path
current_dir = os.path.join(os.path.dirname(__file__))
jnius_config.set_classpath(current_dir + '/java/*')
from jnius import cast, autoclass, JavaException

from .models import Ontology,Entity

# Create your views here.

def index(request):
    ontologies = Ontology.objects.all()
    return render(request, 'ontology/index.html',
                  {'ontologies': ontologies})

def classify(request):
    ontology = None
    if 'entity_name' in request.POST:
        ontology = save_entity(request)
    elif 'new_owner' in request.POST and request.POST['new_owner'] != "":
        owner = request.POST['new_owner']
        ontology, created = Ontology.objects.get_or_create(owner=owner)
    elif 'selected' in request.POST:
        owner = request.POST['selected']
        ontology = Ontology.objects.get(owner=owner)
    else:
        return redirect('index')

    # import any new entities
    if 'entity_file' in request.FILES and request.FILES['entity_file'] != "":
        names = request.FILES['entity_file'].read().splitlines()
        for name in names:
            if name == "":
                continue
            # owlize the entity name
            name = name.replace(" ", "_").replace("'", "")
            name = name.replace("&", "_and_")
            entity, created = Entity.objects.get_or_create(
                name=name,ontology=ontology)
            entity.classified = False
            entity.save()
    
    # load next unclassified entity
    entity = None
    try:
        entity = Entity.objects.filter(classified=False).first()
    except IndexError:
        return redirect('/ontology/')
    if entity == None:
        return redirect('/ontology/')

    # remove the entity from the list of basics
    basics = ontology.roots()
    if entity in basics:
        basics.remove(entity)
        
    return render(request, 'ontology/classify.html',
                  {'ontology': ontology,
                   'entity': entity,
                   'basics': basics})

def load_ontology(request):
    ontology_file = request.FILES['ontology']
    owner = request.POST['new_owner']
    ontology, created = Ontology.objects.get_or_create(owner=owner)

    # load the OWL ontology
    Manager = autoclass('org.semanticweb.owlapi.apibinding.OWLManager')
    mgr = Manager.createOWLOntologyManager()
    Stream = autoclass('java.io.ByteArrayInputStream')
    bst = Stream(ontology_file.read())
    ist = cast('java.io.InputStream', bst)
    ont = mgr.loadOntologyFromOntologyDocument(ist);
    Reasoner = autoclass('org.semanticweb.HermiT.Reasoner')
    rnr = Reasoner(ont)
    
    # process the classes and relations in ontology
    classes = ont.getClassesInSignature()
    for c in classes.toArray():
        entity_name = c.getIRI().getFragment()
        if entity_name == "Thing":
            continue
        entity, created = Entity.objects.get_or_create(
            name=entity_name, ontology=ontology)
        entity.classified = True
        entity.save()
        
        equivs = rnr.getEquivalentClasses(c).getEntities()
        for e in equivs.toArray():
            other_name = e.getIRI().getFragment()
            if other_name == entity.name:
                continue
            other, created = Entity.objects.get_or_create(
                name=other_name, ontology=ontology)
            other.classified = True
            other.save()
            entity.add_equivalent(other,'U')

        subs = rnr.getSubClasses(c, True).getFlattened()

        for e in subs.toArray():
            other_name = e.getIRI().getFragment()
            if other_name == entity.name or other_name == "Nothing":
                continue
            other, created = Entity.objects.get_or_create(
                name=other_name, ontology=ontology)
            other.classified = True
            other.save()

            entity.add_subclass(other, 'U')

    entities = []
    all_entities = Entity.objects.filter(ontology=ontology)
    for entity in all_entities:
        if not entity.has_superclasses():
            entities.append(entity)

    return render(request, 'ontology/ontology.html',
                  {'entities': entities})

def save_entity(request):
    entity_name = request.POST['entity_name']
    owner = request.POST['ontology']
    ontology = Ontology.objects.get(owner=owner)
    entity, created = Entity.objects.get_or_create(
        name=entity_name, ontology=ontology)
    entity.classified = True
    entity.save()

    # create singular entity, link to plural
    if 'plural' in request.POST:
        singular_name = request.POST['singular']
        singular = Entity(name=singular_name,ontology=ontology)
        singular.classified = True
        singular.save()
        singular.add_equivalent(entity, 'P')
        entity = singular

    # create remaining relationships
    for key in request.POST:
        print key
        if not key.startswith('rel.') or request.POST[key] == "":
            continue
        rel_entity = Entity.objects.get(name=key[4:],ontology=ontology)
        rel = request.POST[key]
        if rel == 'H' or rel == 'A' or rel == 'M':
            rel_entity.add_subclass(entity, rel)
        elif rel == '_H' or rel == '_A' or rel == '_M':
            entity.add_subclass(rel_entity, rel[1:])
        elif rel == 'S' or rel == 'E' or rel == 'T':
            entity.add_equivalent(rel_entity, rel)

    return ontology

def subclasses(request):
    subclasses = []
    
    if 'name' in request.GET:
        entity_name = request.GET['name']
        entity = Entity.objects.get(name=entity_name)
        if entity is not None and entity.subclasses is not None:
            subclasses = entity.get_subclasses()
            
    return render(request, 'ontology/subclasses.html',
                  {'subclasses': subclasses})

def show(request):
    owner = request.POST['selected']
    ontology = Ontology.objects.get(owner=owner)
    entities = ontology.roots()
    return render(request, 'ontology/ontology.html',
                  {'entities': entities})
