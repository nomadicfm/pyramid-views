Form View
=========

.. automodule:: pyramid_views.views.edit

    .. autoclass:: FormView

        .. autoattribute:: success_url

        .. autoattribute:: form_class
        .. automethod:: get_form_class
        .. automethod:: get_form

        .. automethod:: form_invalid
        .. automethod:: form_valid

            .. note::

                Override this method if you wish to perform an action
                on successful form submission (Eg: For a contact form
                you may wish to send an email).

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