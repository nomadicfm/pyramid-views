import re
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.query import Query
import sys


class ImproperlyConfigured(Exception):
    """Views are somehow improperly configured"""
    pass


class MultiplePrimaryKeysFound(Exception):
    """Multiple primary keys were found on a model, which is not supported"""
    pass


class TemplateModuleNotFound(Exception):
    """The template module could not be found for a given model"""
    pass


class classonlymethod(classmethod):
    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError("This method is available only on the view class.")
        return super(classonlymethod, self).__get__(instance, owner)


def _(val):
    """Dummy placeholder for translation function used in Django code

    May implement late
    """
    return val


def model_from_query(query):
    return query._primary_entity.entities[0]


def get_model_from_obj(obj):
    if isinstance(obj, Query):
        model = model_from_query(obj)
    elif hasattr(obj, '__table__'):
        model = obj
    else:
        raise ValueError('Expected model or Query object, but got %s' % obj)

    return model


def get_pk_field(obj):
    model = get_model_from_obj(obj)
    primary_keys = [key.name for key in class_mapper(model).primary_key]
    if len(primary_keys) != 1:
        raise MultiplePrimaryKeysFound('Only models with a single primary key are supported by pyramid_views')
    return getattr(model, primary_keys[0])


def get_field(obj, field_name):
    model = get_model_from_obj(obj)
    return getattr(model, field_name)


def get_template_package(obj):
    package_name = get_template_package_name(obj)
    return sys.modules[package_name]


def get_template_package_name(obj):
    """Get the template package for a given model/view"""
    module_name = obj.__module__
    matches = re.match(r'(.*)\.(.*?)', module_name)
    if not matches:
        raise TemplateModuleNotFound('Could not determine template module for model %s in module %s' % (obj, module_name))
    return matches.group(1)