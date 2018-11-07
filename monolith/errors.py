from flask import make_response, render_template
from monolith.views.home import index

def render_error_page(e):
    # TODO
    """
    This function is a callback and it is called when an HTTPExcpetion is thrown
    We will decide in future how to manage different errors
    """
    # return make_response(render_template('error_page.html', exception=e), e.code)
    print(e)
    return make_response(index(), e.code)
