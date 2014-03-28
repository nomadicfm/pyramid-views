Create View
===========

.. automodule:: pyramid_views.views.edit

    .. autoclass:: CreateView

        .. autoattribute:: success_url

            The URL to redirect to upon successful object creation.

        .. autoattribute:: fields

            Fields which should be presented to the user. If ``None``, all fields
            will be available with certain `field exclusion rules`_.

            .. important::

                It is highly recommended you specify this field in order to prevent
                fields becoming unintentionally presented to the user.

        .. autoattribute:: model

            The model of which an instance will be created.

        .. autoattribute:: query
        .. automethod:: get_query
        .. automethod:: get_object

        .. autoattribute:: slug_field
        .. automethod:: get_slug_field
        .. autoattribute:: slug_url_kwarg
        .. autoattribute:: pk_url_kwarg

        .. autoattribute:: form_class
        .. automethod:: get_form_class
        .. automethod:: get_form

        .. automethod:: form_invalid
        .. automethod:: form_valid

        .. autoattribute:: prefix
        .. automethod:: get_prefix

        .. autoattribute:: initial
        .. automethod:: get_initial

        .. automethod:: get_form_kwargs

        .. autoattribute:: template_name
        .. autoattribute:: content_type
        .. automethod:: get_context_data
        .. autoattribute:: macro_names
        .. automethod:: get_macro_names

        .. automethod:: get
        .. automethod:: post


.. _field exclusion rules: http://wtforms-alchemy.readthedocs.org/en/latest/column_conversion.html#excluded-fields