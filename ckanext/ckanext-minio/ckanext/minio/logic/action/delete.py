from ckan.types.logic import ActionResult
from typing import Any, Union, cast

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic
from ckanext.minio.logic.minio_con import MinioConnection

from ckan.types import Context, DataDict, ErrorDict

ValidationError = ckan.logic.ValidationError
NotFound = ckan.logic.NotFound
_get_or_bust = ckan.logic.get_or_bust
_check_access = ckan.logic.check_access
_get_action = ckan.logic.get_action
minio_connection = MinioConnection()

#Xoá resource
def resource_minio_delete(context: Context, data_dict: DataDict) -> ActionResult.ResourceDelete:
    model = context['model']
    id = _get_or_bust(data_dict, 'id')

    entity = model.Resource.get(id)

    if entity is None:
        raise NotFound

    _check_access('resource_delete', context, data_dict)

    # Perform Minio deletion logic if applicable
    if minio_connection.is_enabled():
        client = minio_connection.get_client()

        try:
            resource = toolkit.get_action('resource_show')(context, {'id': id})
            package_id = resource.get('package_id')
            package = toolkit.get_action('package_show')(context, {'id': package_id})
            package_name = package.get('name')

            if resource.get('url_type') == 'upload':
                bucket_name = minio_connection.get_bucket_name()
                object_name = f'{package_name}/{resource["id"]}'

                try:
                    client.remove_object(bucket_name=bucket_name, object_name=object_name)
                except Exception as e:
                    errors = {'resource_delete': [f"Error deleting resource from Minio: {str(e)}"]}
                    raise ValidationError(errors)
        except NotFound:
            raise ValidationError({"resource_delete": ["Resource or package not found"]})

    package_id = entity.get_package_id()

    pkg_dict = _get_action('package_show')(context, {'id': package_id})

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.before_resource_delete(context, data_dict, pkg_dict.get('resources', []))

    package_show_context: Union[Context, Any] = dict(context, for_update=True)
    pkg_dict = _get_action('package_show')(
        package_show_context, {'id': package_id})

    if pkg_dict.get('resources'):
        pkg_dict['resources'] = [r for r in pkg_dict['resources'] if not r['id'] == id]
    try:
        pkg_dict = _get_action('package_update')(context, pkg_dict)
    except ValidationError as e:
        errors = cast("list[ErrorDict]", e.error_dict['resources'])[-1]
        raise ValidationError(errors)

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.after_resource_delete(context, pkg_dict.get('resources', []))

    model.repo.commit()
    
#Xoá dataset khi purge
def dataset_minio_purge(context: Context, data_dict: DataDict) -> ActionResult.DatasetPurge:
    from sqlalchemy import or_

    model = context['model']
    id = _get_or_bust(data_dict, 'id')

    pkg = model.Package.get(id)
    if pkg is None:
        raise NotFound('Dataset was not found')
    context['package'] = pkg

    _check_access('dataset_purge', context, data_dict)

    # Minio deletion logic
    if minio_connection.is_enabled():
        client = minio_connection.get_client()
        package_name = pkg.name
        bucket_name = toolkit.config.get('ckanext_minio.bucket_name', 'ckan')

        try:
            # List and delete all objects in the Minio bucket related to the package
            objects = client.list_objects(bucket_name, prefix=f'{package_name}/', recursive=True)
            for obj in objects:
                client.remove_object(bucket_name, obj.object_name)
        except Exception as e:
            raise ValidationError({'dataset_purge': ['Error deleting package folder in Minio: ' + str(e)]})

    # Purge dataset members
    members = model.Session.query(model.Member) \
                   .filter(model.Member.table_id == pkg.id) \
                   .filter(model.Member.table_name == 'package')
    if members.count() > 0:
        for m in members.all():
            m.purge()

    # Purge package relationships
    for r in model.Session.query(model.PackageRelationship).filter(
            or_(model.PackageRelationship.subject_package_id == pkg.id,
                model.PackageRelationship.object_package_id == pkg.id)).all():
        r.purge()

    # Purge the dataset
    pkg = model.Package.get(id)
    assert pkg
    pkg.purge()
    model.repo.commit_and_remove()