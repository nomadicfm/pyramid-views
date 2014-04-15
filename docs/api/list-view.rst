List View
=========

.. automodule:: pyramid_views.views.list

    .. autoclass:: ListView

        .. autoattribute:: model
        .. autoattribute:: query
        .. automethod:: get_query

        .. autoattribute:: template_name
        .. autoattribute:: template_extension
        .. autoattribute:: content_type
        .. autoattribute:: template_name_suffix

        .. automethod:: get_context_data
        .. automethod:: get_context_object_name

        .. autoattribute:: allow_empty
        .. automethod:: get_allow_empty

        .. autoattribute:: db_session

        .. autoattribute:: macro_names
        .. automethod:: get_macro_names

        .. autoattribute:: paginate_by
        .. automethod:: get_paginate_by

        .. autoattribute:: paginate_orphans
        .. automethod:: get_paginate_orphans

        .. autoattribute:: page_kwarg
        .. automethod:: get