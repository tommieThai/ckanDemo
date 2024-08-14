from ckan.types.logic import ActionResult
import os
import logging
from typing import Any, Union, cast

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic
import ckan.logic as logic
from ckanext.minio.logic.minio_con import MinioConnection

from ckan.types import Context, DataDict, ErrorDict
from ckan.common import _

log = logging.getLogger(__name__)

ValidationError = ckan.logic.ValidationError
NotFound = logic.NotFound
_get_or_bust = logic.get_or_bust
_check_access = logic.check_access
_get_action = logic.get_action
minio_connection = MinioConnection()

def resource_minio_update(context: Context, data_dict: DataDict) -> ActionResult.ResourceUpdate:

    model = context['model']
    id: str = _get_or_bust(data_dict, "id")

    if not data_dict.get('url'):
        data_dict['url'] = ''

    resource = model.Resource.get(id)
    if resource is None:
        raise NotFound('Resource was not found.')
    context["resource"] = resource
    old_resource_format = resource.format

    if not resource:
        log.debug('Could not find resource %s', id)
        raise NotFound(_('Resource was not found.'))

    _check_access('resource_update', context, data_dict)
    del context["resource"]

    package_id = resource.package.id
    package_show_context: Union[Context, Any] = dict(context, for_update=True)
    pkg_dict = _get_action('package_show')(package_show_context, {'id': package_id})

    resources = cast("list[dict[str, Any]]", pkg_dict['resources'])
    for n, p in enumerate(resources):
        if p['id'] == id:
            break
    else:
        log.error('Could not find resource %s after all', id)
        raise NotFound(_('Resource was not found.'))

    # Minio update logic
    if minio_connection.is_enabled() and 'upload' in data_dict:
        client = minio_connection.get_client()
        new_file = data_dict.get('upload')
        package_name = pkg_dict.get('name')

        if resource.url_type == 'upload':
            bucket_name = toolkit.config.get("ckanext_minio.bucket_name", "ckan")
            object_name = f'{package_name}/{resource.id}'

            try:
                tmp_filepath = '/tmp/' + new_file.filename
                new_file.save(tmp_filepath)

                client.fput_object(
                    bucket_name=bucket_name, 
                    object_name=object_name, 
                    file_path=tmp_filepath, 
                    content_type=new_file.mimetype
                )

                os.remove(tmp_filepath)
            except Exception as e:
                errors = f'{"resource_update": ["Error updating resource in Minio: " + str(e)]}'
                raise ValidationError(errors)

    # Persist the datastore_active extra if already present and not provided
    if ('datastore_active' in resource.extras and
            'datastore_active' not in data_dict):
        data_dict['datastore_active'] = resource.extras['datastore_active']

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.before_resource_update(context, pkg_dict['resources'][n], data_dict)

    resources[n] = data_dict

    try:
        context['use_cache'] = False
        updated_pkg_dict = _get_action('package_update')(context, pkg_dict)
    except ValidationError as e:
        try:
            error_dict = cast("list[ErrorDict]", e.error_dict['resources'])[n]
        except (KeyError, IndexError):
            error_dict = e.error_dict
        raise ValidationError(error_dict)

    resource = _get_action('resource_show')(context, {'id': id})

    if old_resource_format != resource['format']:
        _get_action('resource_create_default_resource_views')(
            {'model': context['model'], 'user': context['user'],
             'ignore_auth': True},
            {'package': updated_pkg_dict,
             'resource': resource})

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.after_resource_update(context, resource)

    return resource

