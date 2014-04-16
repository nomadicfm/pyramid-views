from __future__ import unicode_literals

from sqlalchemy.orm import Query
from sqlalchemy.orm.exc import NoResultFound

from pyramid import httpexceptions

from pyramid_views.utils import ImproperlyConfigured, _
from pyramid_views.views.base import TemplateResponseMixin, ContextMixin, View, DbSessionMixin, MacroMixin
from pyramid_views import utils

class SingleObjectMixin(DbSessionMixin, ContextMixin):
    """
    Provides the ability to retrieve a single object for further manipulation.
    """
    model = None
    query = None
    slug_field = 'slug'
    context_object_name = None
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def get_object(self, query=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.query` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom query if provided; this is required for subclasses
        # like DateDetailView
        if query is None:
            query = self.get_query()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if pk is not None:
            pk_field = utils.get_pk_field(query)
            query = query.filter(pk_field==pk)

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = utils.get_field(query, self.get_slug_field())
            query = query.filter(slug_field==slug)

        # If none of those are defined, it's an error.
        else:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered query
            obj = query.one()
        except NoResultFound:
            raise httpexceptions.HTTPNotFound(_("No %(verbose_name)s found matching the query") %
                                            {'verbose_name': utils.model_from_query(query).__name__})
        return obj

    def get_query(self):
        """
        Return the `Query` that will be used to look up the object.

        Note that this method is called by the default implementation of
        `get_object` and may not be called if `get_object` is overriden.
        """
        if self.query is None:
            if self.model:
                return self.db_session.query(self.model)
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a Query. Define "
                    "%(cls)s.model, %(cls)s.query, or override "
                    "%(cls)s.get_query()." % {
                        'cls': self.__class__.__name__
                    }
                )

        # Set the session on the query if it doesn't have one
        if isinstance(self.query, Query) and not self.query.session:
            self.query.session = self.db_session

        return self.query

    def get_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.slug_field

    def get_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.context_object_name:
            return self.context_object_name
        # Is this a model
        elif hasattr(obj, '__table__'):
            return obj.__table__.name
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context.update(kwargs)
        return super(SingleObjectMixin, self).get_context_data(**context)


class BaseDetailView(SingleObjectMixin, View):
    """
    A base view for displaying a single object
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class SingleObjectTemplateResponseMixin(TemplateResponseMixin):
    template_name_field = None
    template_name_suffix = '_detail'
    template_extension = '.pt'

    def get_template_names(self):
        """
        Return a list of template names to be used for the request. May not be
        called if render_to_response is overridden. Returns the following list:

        * the value of ``template_name`` on the view (if provided)
        * the contents of the ``template_name_field`` field on the
          object instance that the view is operating upon (if available)
        * ``<app_label>/<model_name><template_name_suffix>.html``
        """
        try:
            names = super(SingleObjectTemplateResponseMixin, self).get_template_names()
        except ImproperlyConfigured:
            # If template_name isn't specified, it's not a problem --
            # we just start with an empty list.
            names = []

            # If self.template_name_field is set, grab the value of the field
            # of that name from the object; this is the most specific template
            # name, if given.
            if self.object and self.template_name_field:
                name = getattr(self.object, self.template_name_field, None)
                if name:
                    names.insert(0, name)

            # The least-specific option is the default <app>/<model>_detail.html;
            # only use this if the object in question is a model.
            if hasattr(self.object, '__table__'):
                template_package = utils.get_template_package_name(self.object)
                names.append("%s:templates/%s%s%s" % (
                    template_package,
                    self.object.__tablename__,
                    self.template_name_suffix,
                    self.template_extension
                ))
            elif hasattr(self, 'model') and self.model is not None and hasattr(self.model, '__tablename__'):
                template_package = utils.get_template_package_name(self.model)
                names.append("%s:templates/%s%s%s" % (
                    template_package,
                    self.model.__tablename__,
                    self.template_name_suffix,
                    self.template_extension
                ))

            # If we still haven't managed to find any template names, we should
            # re-raise the ImproperlyConfigured to alert the user.
            if not names:
                raise

            # For benefit of tests
            self._template_names = names

        return names


class DetailView(SingleObjectTemplateResponseMixin, MacroMixin, BaseDetailView):
    """
    Render a "detail" view of an object.

    By default this is a model instance looked up from ``self.query``, but the
    view will support display of *any* object by overriding ``self.get_object()``.
    """
