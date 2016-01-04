from django.db import models

# Create your models here.

class Ontology(models.Model):
    class Meta:
        verbose_name_plural = "ontologies"
    owner = models.CharField(max_length=200)

    def entities(self):
        return Entity.objects.filter(ontology_id=self.id)
    
    def basics(self):
        return Entity.objects.filter(ontology_id=self.id).filter(weight__gte=10)
    def roots(self):
        entities = Entity.objects.filter(ontology=self)
        roots = []
        for e in entities:
            if not e.has_superclasses():
                roots.append(e)
                #print "%s, %s" % (e.name, e.get_superclasses())
        return roots
    
    def __str__(self):
        return self.owner
    
class Entity(models.Model):
    class Meta:
        verbose_name_plural = "entities"
    name = models.CharField(max_length=200)
    weight = models.IntegerField(default=0)
    ontology = models.ForeignKey(Ontology)
    classified = models.BooleanField(default=False)
    subclasses = models.ManyToManyField('self', through='SubClassOf',
                                        symmetrical=False,
                                        related_name='subclass_of')
    equivalants = models.ManyToManyField('self', through='EquivalentTo',
                                        symmetrical=False,
                                        related_name='equivalent_to+')

    def add_equivalent(self, entity, heuristic):
        equivalent, created = EquivalentTo.objects.get_or_create(
            from_entity=self,
            to_entity=entity,
            heuristic=heuristic)

        # create the inverse relationship
        EquivalentTo.objects.get_or_create(
            from_entity=entity,
            to_entity=self,
            heuristic=heuristic)
        return equivalent

    def add_subclass(self, entity, heuristic):
        subclass, created = SubClassOf.objects.get_or_create(
            from_subclass=entity,
            to_class=self,
            heuristic=heuristic)
        
    def get_equivalents(self):
        return self.equivalents.filter(to_entities__from_entity=self)

    def has_equivalents(self):
        return self.equivalents.filter(to_entities__from_entity=self).count() > 0
    
    def get_subclasses(self):
        return self.subclass_of.filter(from_subclasses__to_class=self)

    def has_subclasses(self):
        return self.subclass_of.filter(from_subclasses__to_class=self).count() > 0

    def has_superclasses(self):
        return self.subclasses.filter(to_classes__from_subclass=self).count() > 0

    def get_superclasses(self):
        return self.subclasses.filter(to_classes__from_subclass=self)

    def __str__(self):
        return self.name
    
class SubClassOf(models.Model):
    HEURISTICS = (
        ('H', 'Hypernym'),
        ('M', 'Meryonym'),
        ('A', 'Attribute'),
        ('U', 'Unknown'),
    )
    
    class Meta:
        verbose_name_plural = "subclasses"

    from_subclass = models.ForeignKey(Entity, related_name='from_subclasses')
    to_class = models.ForeignKey(Entity, related_name='to_classes')
    heuristic = models.CharField(max_length=1, choices=HEURISTICS, default='H')

    def __str__(self):
        return self.from_subclass.name + " SubClassOf " + self.to_class.name

class EquivalentTo(models.Model):
    HEURISTICS = (
        ('S', 'Synonym'),
        ('P', 'Plural'),
        ('E', 'Event'),
        ('T', 'Technology'),
        ('U', 'Unknown'),
    )
        
    class Meta:
        verbose_name_plural = "equivalencies"
    from_entity = models.ForeignKey(Entity, related_name='from_entities')
    to_entity = models.ForeignKey(Entity, related_name='to_entities')
    heuristic = models.CharField(max_length=1, choices=HEURISTICS)

    def __str__(self):
        return self.from_entity.name + " EquivalentTo " + self.to_entity.name
