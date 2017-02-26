from django.db import models
from settings_viewer import DICT_SETTINGS_VIEWER
import importlib
module_custom = importlib.import_module(DICT_SETTINGS_VIEWER['app_label']+'.models')
model_custom = getattr(module_custom, DICT_SETTINGS_VIEWER['model_name'])

class m_Entity(models.Model):
    id_item = models.CharField(max_length=200, unique=True, db_index=True)

class m_Tag(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#000000")
    m2m_custom_model = models.ManyToManyField(model_custom, related_name='viewer_tags')
    m2m_entity = models.ManyToManyField(m_Entity, related_name='viewer_tags')

    def __str__(self):
        return '<Tag [%s]>' % (self.name)