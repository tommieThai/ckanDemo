
def new_template_hello():
    return "Hello, new_template!"


def get_helpers():
    return {
        "new_template_hello": new_template_hello,
    }
