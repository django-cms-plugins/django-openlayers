from django.db import models

import re
import unicodedata
import json

def getSlug(s):
    slug = unicodedata.normalize('NFKD', s)
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '', slug).strip('-')
    slug = re.sub(r'[-]+', '', slug)
    return slug

VECTOR_LAYERS_TYPES = (
    ('kml', 'KML layer'),
    #('wfs', 'wfs layer'),
)

RASTER_LAYERS_TYPES = (
    ('OSM', 'OSM layer'),
    ('GOOGLE-STREET', 'Google street'),
    ('GOOGLE-SATELLITE', 'Google satellite'),
    ('GOOGLE-TERRAIN', 'Google terrain'),
    ('GOOGLE-HYBRID', 'Google hybrid'),
    
)

JS_BOOL_CHOICES = (
    ('true', 'True'),
    ('false', 'False'),
)





    
class _Layer(models.Model):

    name = models.CharField(null=False, blank=False, unique=True, max_length=200)
    description = models.TextField(null=True, blank=True)
    options = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        
    def __unicode__(self):
        return u'%s' % (self.name)
        
        
class RasterLayer(_Layer):
    
    #maps = models.ManyToManyField(Map, related_name='raster_layers', null=True, blank=True)
    type = models.CharField(max_length=300, choices = RASTER_LAYERS_TYPES)
    

class VectorLayer(_Layer):
    
    #maps = models.ManyToManyField(Map, related_name='vector_layers', null=True, blank=True)
    type = models.CharField(max_length=300, choices = VECTOR_LAYERS_TYPES)
    layer_uri =  models.CharField(null=True, blank=True, max_length=300)
    
    #layer options
    extract_styles = models.CharField(choices = JS_BOOL_CHOICES, default="true", max_length=10);
    extract_attributes = models.CharField(choices = JS_BOOL_CHOICES, default="true", max_length=10);    
    
    #popup_handler = models.BooleanField(default=False)



class Map(models.Model):
    
    name = models.CharField(null=False, blank=False, unique=True, max_length=200)
    description = models.TextField(null=True, blank=True)
    
    raster_layers = models.ManyToManyField(RasterLayer, through='MapsRasterLayers')
    vector_layers = models.ManyToManyField(VectorLayer, through='MapsVectorLayers')
    
    navigation_control = models.BooleanField(default=True)
    layer_switcher_control = models.BooleanField(default=False)
    scale_line_control = models.BooleanField(default=False)
    pan_zoom_bar_control = models.BooleanField(default=False)
    
    @property
    def ordered_raster_layers(self):
        return self.raster_layers.order_by('mapsrasterlayers__order')
        
    @property
    def ordered_vector_layers(self):
        return self.vector_layers.order_by('mapsvectorlayers__order')


    def getDivId(self):
        return getSlug(self.name)
        
    #this is an alternate approach for generating js.
    #still thinking about using it.
    def getJsonOptions(self):
        map_name = "map-"+str(map.id)
        map_options = {}
        map_controls = []
        if self.navigation_control:
            map_controls.append("new OpenLayers.Control.Navigation()")
        if self.pan_zoom_bar_control:
            map_controls.append("new OpenLayers.Control.PanZoomBar()")
        if self.layer_switcher_control:
            map_controls.append("new OpenLayers.Control.LayerSwitcher()")
        if self.scale_line_control:
            map_controls.append("new OpenLayers.Control.ScaleLine()")

        map_options['controls'] = map_controls
        out = [map_name, map_options]

        return json.dumps(out);



class MapsRasterLayers(models.Model):

    map = models.ForeignKey(Map)
    layer = models.ForeignKey(RasterLayer)
    order = models.IntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ('order',)
    

class MapsVectorLayers(models.Model):

    map = models.ForeignKey(Map)
    layer = models.ForeignKey(VectorLayer)
    order = models.IntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ('order',)


class UploadedFile(models.Model):
    file = models.FileField(upload_to='openlayers')
    description = models.TextField(null=True, blank=True)


try:
    import cms
    from cms_models import *
except:
    pass


