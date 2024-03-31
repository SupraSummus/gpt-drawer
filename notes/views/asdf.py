from django.http import HttpResponse

from djsfc import Router, parse_template


router = Router(__name__)
template_str = '''\
<!-- asdf {% url ':test' %} -->
'''
template = parse_template(template_str, router)


@router.route('GET', 'test/')
def test(request):
    return HttpResponse('test')
