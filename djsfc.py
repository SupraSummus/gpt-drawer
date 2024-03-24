import django
from django import template


class Router:
    def __init__(self):
        self.patterns = {}
        self.sub_routers = {}

    def route(self, method, pattern):
        def decorator(view_func):
            view_name = view_func.__name__
            handlers = self.patterns.setdefault(pattern, {})
            if method in handlers:
                raise ValueError(f'Handler for {method} {pattern} already exists: {handlers[method]}')
            handlers[method] = (view_func, view_name)
            return view_func
        return decorator

    def route_all(self, pattern, sub_router, name=None):
        self.sub_routers[pattern] = (sub_router, name)

    @property
    def urls(self):
        urls = []

        for pattern, handlers in self.patterns.items():
            view_func = MethodDispatchView(handlers)
            # we need to include view_func multiple times to get multiple names
            for method, (_, name) in handlers.items():
                urls.append(django.urls.path(
                    pattern,
                    view_func,
                    name=name,
                ))

        for pattern, (sub_router, name) in self.sub_routers.items():
            sub_urls = sub_router.urls
            urls.append(django.urls.path(
                pattern,
                django.urls.include((sub_urls, name), namespace=name),
            ))

        return urls


class MethodDispatchView:
    def __init__(self, handlers):
        self.handlers = handlers

    def __call__(self, request, *args, **kwargs):
        handler = self.handlers.get(request.method)
        if handler is None:
            return django.http.HttpResponseNotAllowed(self.handlers.keys())
        view_func, _ = handler
        return view_func(request, *args, **kwargs)


register = template.Library()


class AddNamespaceFilterExpression:
    def __init__(self, filter_expression):
        self.filter_expression = filter_expression

    def resolve(self, context):
        resolved = self.filter_expression.resolve(context)
        if resolved.startswith(':'):
            return context['request'].resolver_match.namespace + resolved
        return resolved


@register.tag
def url(parser, token):
    node = django.template.defaulttags.url(parser, token)
    node.view_name = AddNamespaceFilterExpression(node.view_name)
    return node


def get_template_block(template, block_name):
    assert isinstance(template, django.template.backends.django.Template)
    node = get_block_from_nodelist(template.template.nodelist, block_name)
    if not node:
        raise ValueError(f'Block {block_name} not found in template')
    return django.template.backends.django.Template(PartialTemplate(
        node.nodelist,
        engine=template.backend.engine,
    ), template.backend)


class PartialTemplate(django.template.base.Template):
    def __init__(self, nodelist, engine):
        self.nodelist = nodelist
        self.engine = engine
        self.name = None


def get_block_from_nodelist(nodelist, block_name):
    for node in nodelist:
        if isinstance(node, django.template.loader_tags.BlockNode) and node.name == block_name:
            return node
        if hasattr(node, 'nodelist'):
            ret = get_block_from_nodelist(node.nodelist, block_name)
            if ret is not None:
                return ret
    return None
