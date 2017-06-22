from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_filters(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_filters']

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_tags(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_tags']

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_settings(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_settings']
 
@register.simple_tag(takes_context=True)
def get_values_filter(context, filter_custom):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__viewer__filter_custom'][filter_custom['data_field']]

@register.simple_tag(takes_context=True)
def get_tags(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__viewer__filter_tags']

@register.filter
def in_columns_checked(key, request):
    current_corpus = request.session['viewer__viewer__current_corpus']
    return key in request.session[current_corpus]['viewer__viewer__columns']

@register.filter
def get_is_filter_for_alphanumeric(key, settings):
    # current_corpus = request.session['viewer__viewer__current_corpus']
    # return key in request.session[current_corpus]['viewer__viewer__columns']
    return settings['data_fields'][key]['type'] == 'string' or settings['data_fields'][key]['type'] == 'text'

@register.filter
def get(item, field):
    try:
        return item[field]
    except TypeError:
        return getattr(item, field)

@register.filter
def get_type_field(field, settings):
    return settings['data_fields'][field]['type'].lower()

@register.filter
def get_display_name(field, settings):
    return settings['data_fields'][field]['display_name']

@register.filter
def display_as_tag_classes(list_tags):
    result = ''

    try:
        for tag in list_tags:
            result += 'tag_' + str(tag.id) + ' '
    except TypeError:
        for tag in list_tags.all():
            result += 'tag_' + str(tag.id) + ' '

    return result.strip()
