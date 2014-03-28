Delete View
===========

.. automodule:: pyramid_views.views.edit

    .. autoclass:: DeleteView

        .. autoattribute:: success_url

            The URL to redirect to upon successful deletion.

        .. autoattribute:: model

            The model of which an instance will be deleted.

        .. autoattribute:: query

            Limit deletion to only objects provided by ``query``. If you specify this
            then you can omit ``model``.

        .. automethod:: get_query
        .. automethod:: get_object

        .. autoattribute:: slug_field
        .. automethod:: get_slug_field
        .. autoattribute:: slug_url_kwarg
        .. autoattribute:: pk_url_kwarg

        .. autoattribute:: template_name
        .. autoattribute:: content_type
        .. automethod:: get_context_data
        .. autoattribute:: macro_names
        .. automethod:: get_macro_names

        .. automethod:: get
        .. automethod:: post


.. _field exclusion rules: http://wtforms-alchemy.readthedocs.org/en/latest/column_conversion.html#excluded-fields