from __future__ import unicode_literals

import logging
from functools import update_wrapper

from pyramid import httpexceptions
from pyramid.renderers import render_to_response, get_renderer
from pyramid.response import Response
from zope.interface.interfaces import ComponentLookupError

from pyramid_views.utils import ImproperlyConfigured, classonlymethod, get_template_package
import pyramid_views

logger = logging.getLogger('django.request')


class ContextMixin(object):
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data as the template context.
    """

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        self._context = kwargs
        return kwargs


class MacroMixin(object):
    macro_names = None

    def get_macro_names(self):
        """
        Return a directory of macro names.

        Values should be template paths, and keys will be used
        as the lookup key in the template. Eg. ``macros.<key>.<macro>``.
        """
        return self.macro_names or {}

    def get_macros(self):
        macro_names = self.get_macro_names()
        macros = {}
        for k, macro_name in macro_names.items():
            template = get_renderer(macro_name).implementation()
            if hasattr(template, 'macros'):
                macros[k] = template.macros
        return macros

    def get_context_data(self, **kwargs):
        context = super(MacroMixin, self).get_context_data(**kwargs)
        context['macros'] = self.get_macros()
        return context


class DbSessionMixin(object):
    """
    A default db session mixin which will provide access to the
    application's scoped database session
    """

    @property
    def db_session(self):
        if pyramid_views.session:
            return pyramid_views.session()
        else:
            raise ImproperlyConfigured("DB session not available. Either set the view's 'session' "
                                       "attribute, or call pyramid_views.configure_views() with a "
                                       "scoped session.")


class View(object):
    """
    Intentionally simple parent class for all views. Only implements
    dispatch-by-method and simple sanity checking.
    """

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classonlymethod
    def as_view(cls, **initkwargs):
        """
        Main entry point for a request-response process.
        """
        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            # Pass the matchdict into the kwargs so dispatch receives
            # the values as kwargs
            kwargs.update(request.matchdict)
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self.dispatch(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())
        return view

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        response = handler(request, *args, **kwargs)
        # Expose the context if present (for the benefit of testing)
        if hasattr(self, '_context'):
            response.context = self._context
        if hasattr(self, '_template_names'):
            response.template_names = self._template_names
        return response

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
            extra={
                'status_code': 405,
                'request': request
            }
        )

        return httpexceptions.HTTPMethodNotAllowed(headers={'Allow': ', '.join(self._allowed_methods())})

    def options(self, request, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """
        response = Response()
        response.headers['Allow'] = ', '.join(self._allowed_methods())
        response.headers['Content-Length'] = '0'
        return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


class TemplateResponseMixin(object):
    """
    A mixin that can be used to render a template.
    """
    template_name = None
    content_type = None

    def render_to_response(self, context):
        """
        Returns a response for this with a template rendered with the given context.
        """
        response = render_to_response(
            renderer_name=self.get_template_names()[0],
            value=context,
            request=self.request,
            package=get_template_package(self)
        )
        if self.content_type:
            response.content_type = self.content_type
        self._context = context
        return response

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if self.template_name is None:

            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            # Save for later for benefit of testing
            self._template_names = [self.template_name]
            return self._template_names


class TemplateView(DbSessionMixin, TemplateResponseMixin, ContextMixin, MacroMixin, View):
    """
    A view that renders a template.  This view will also pass into the context
    any keyword arguments passed by the url conf.
    """
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = self.render_to_response(context)
        return response


class RedirectView(View):
    """
    A view that provides a redirect on any GET request.
    """
    permanent = True
    url = None
    pattern_name = None
    query_string = False

    def get_redirect_url(self, *elements, **kw):
        """
        Return the URL redirect to. Keyword arguments from the
        URL pattern match generating the redirect request
        are provided as kwargs to this method.
        """
        if self.url:
            url = self.url % kw
        elif self.pattern_name:
            try:
                url = self.request.route_url(self.pattern_name, *elements, **kw)
            except (KeyError, ComponentLookupError):
                return None
        else:
            return None

        args = self.request.query_string
        if args and self.query_string:
            url = "%s?%s" % (url, args)
        return url

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        if url:
            if self.permanent:
                return httpexceptions.HTTPMovedPermanently(url)
            else:
                return httpexceptions.HTTPFound(url)
        else:
            logger.warning('Gone: %s', request.path,
                        extra={
                            'status_code': 410,
                            'request': request
                        })
            return httpexceptions.HTTPGone()

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
