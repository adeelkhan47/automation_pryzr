import re
from functools import wraps

from helpers.response import error


def matches_any_pattern(pattern_list, string_to_match):
    for pattern in pattern_list:
        if re.match(pattern, string_to_match):
            return True
    return False


def check_permission(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        user = kwargs.get("user")
        endpoint = request.url.path
        endpoint = endpoint[7:-1]

        method = request.method
        permissions = [each.permission.endpoint for each in user.role.permissions if each.permission.method == method]
        if matches_any_pattern(permissions, endpoint):
            return route_func(*args, **kwargs)
        else:
            raise error(message="unauthorised user.", code=403)

    return wrapper
