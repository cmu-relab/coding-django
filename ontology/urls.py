from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^classify$', views.classify, name='classify'),
    url(r'^subclasses$', views.subclasses, name='subclasses'),
    url(r'^load_ontology$', views.load_ontology, name='load_ontology'),
    url(r'^show$', views.show, name='show'),
]
