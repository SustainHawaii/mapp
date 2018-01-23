from django import template
import json
register = template.Library()


@register.filter(name='lookup')
def lookup(value, arg):
    if value and arg:
        return value[arg]
    else:
        return ""


@register.filter(name='split')
def split(value, arg):
    print value
    try:
        result = value.split(arg)
    except:
        result = ''
    return result


@register.assignment_tag(name='to_String')
def string_fy(elem):
    return str(elem)


@register.filter(name='json_parse')
def json_parse(value):
    return json.loads(value)


@register.filter(name='jsonify')
def jsonify(value):
    if value:
        return json.dumps(value)

    return ''

@register.filter(name='angular_escape_quotes')
def angular_escape_quotes(value):
    if value:
        return value.replace("'", "\\'").replace('"', '\\"')

    return ''

@register.filter(name='json_load')
def json_load(value):
    try:
        output = json.loads(value)
    except:
        output = ''
    return output


@register.filter(name='check_permission')
def check_permission(user, args):
    permission = False
    permission_type = args.split(',')[0]
    action = args.split(',')[1]
    for ut in user.user_types:
        if permission_type in ut.permissions:
            if action in ut.permissions[permission_type]:
                if ut.permissions[permission_type][action]:
                    permission = True
                    continue

    return permission
