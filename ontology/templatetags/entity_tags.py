from django import template

register = template.Library()

@register.inclusion_tag('ontology/expand_entities.html')
def expand_entities(entities, path, name):
    return {'entities': entities, 'entity_path': path + "." + name}
