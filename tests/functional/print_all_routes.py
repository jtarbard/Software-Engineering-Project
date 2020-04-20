

"""
Routes to test for:
* TODO: Test navbar!!
<Rule '/static/<filename>' (OPTIONS, HEAD, GET) -> static> * TODO: Ask lewis. What route is this?
"""


# Somehow, check all routes have been tested.
# maybe collect all route test functions and have them return the route it's testing for?
# (then check against the list of all rules)
def print_all_routes():
    from main.app import create_app
    import pprint
    for rule in [r for r in create_app().url_map.iter_rules() if "GET" in r.methods]:
        pprint.pprint(rule)
