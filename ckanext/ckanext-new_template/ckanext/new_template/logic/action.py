import ckan.plugins.toolkit as tk
import ckanext.new_template.logic.schema as schema


@tk.side_effect_free
def new_template_get_sum(context, data_dict):
    tk.check_access(
        "new_template_get_sum", context, data_dict)
    data, errors = tk.navl_validate(
        data_dict, schema.new_template_get_sum(), context)

    if errors:
        raise tk.ValidationError(errors)

    return {
        "left": data["left"],
        "right": data["right"],
        "sum": data["left"] + data["right"]
    }


def get_actions():
    return {
        'new_template_get_sum': new_template_get_sum,
    }
