#Nohthing changed here

import ckan.logic as logic
import ckan.authz as authz
from ckan.logic.auth import get_resource_object
from ckan.common import _
from ckan.types import Context, DataDict, AuthResult

def resource_minio_delete_auth(context: Context, data_dict: DataDict) -> AuthResult:
    model = context['model']
    user = context.get('user')
    resource = get_resource_object(context, data_dict)

    # check authentication against package
    assert resource.package_id
    pkg = model.Package.get(resource.package_id)
    if not pkg:
        raise logic.NotFound(_(
            'No package found for this resource, cannot check auth.'))

    pkg_dict = {'id': pkg.id}
    authorized = authz.is_authorized(
        'package_delete', context, pkg_dict).get('success')

    if not authorized:
        return {'success': False, 'msg': _(
            'User %s not authorized to delete resource %s'
        ) % (user, resource.id)}
    else:
        return {'success': True}

def dataset_minio_purge_auth(context: Context, data_dict: DataDict) -> AuthResult:
    # Only sysadmins are authorized to purge datasets
    return {'success': False}