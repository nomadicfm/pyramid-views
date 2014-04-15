Introduction
============

.. highlight::python

Class-based generic views?
--------------------------

So what are class-based generic views? A generic view is one which provides generic
functionality. Implementing these types of views with classes allows the
developer to customise this behaviour.

A simple example::

    from pyramid_views import views
    # An example TemplateView which simply renders the home template
    class HomeView(views.TemplateView):
        template_name = 'templates/home.pt'

And to add a route::

    config.add_route('home', '/', HomeView.as_view())

Why?
----

The motivation here is to allow for flexible views while removing
the need for boiler-plate code.

Differences from Django
-----------------------

The functionality here is a direct port of `Django's class-based views`_, so those
docs are the recommended reference point.

However, there are a few differences to note:

* Any reference to the term ``queryset`` has changed to ``query``. For example:

    * ``get_queryset()`` is now ``get_query()``
    * The ``queryset`` attribute is now the ``query`` attribute

* The ``__all__`` value for the ``fields`` attribute is unsupported. Omit the
  ``fields`` attribute entirely for the same behaviour.

**Additional functionality** includes:

* The ``MacroMixin`` class, for passing macros to `chameleon`_ templates via the ``macro_names`` attribute.
* The ``DbSessionMixin`` class makes the database session available via ``self.db_session``


.. _Django's class-based views: https://docs.djangoproject.com/en/1.7/ref/class-based-views/
.. _chameleon: http://chameleon.readthedocs.org/en/latest/