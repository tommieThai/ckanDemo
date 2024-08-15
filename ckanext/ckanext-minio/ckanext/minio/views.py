
import flask
from flask import Blueprint, redirect
from typing import Any, Optional, Union
from werkzeug.wrappers.response import Response as WerkzeugResponse
from ckan.types import Context, Response
from ckan.common import _, config, g, request, current_user
import ckan.logic as logic
import ckan.lib.base as base
from ckan.lib.helpers import helper_functions as h
from ckan.lib import signals
import ckan.lib.uploader as uploader
import urllib.request
from ckanext.minio.logic.minio_con import MinioConnection

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
check_access = logic.check_access
get_action = logic.get_action


minio_download = Blueprint(
    "minio_download",
      __name__, 
      url_prefix=u'/dataset/<id>/resource',
      url_defaults={u'package_type': u'dataset'}
      )


def download(package_type: str,
             id: str,
             resource_id: str,
             filename: Optional[str] = None
             ) -> Union[Response, WerkzeugResponse]:

    context: Context = {
        u'user': current_user.name,
        u'auth_user_obj': current_user
    }

    try:
        rsc = get_action(u'resource_show')(context, {u'id': resource_id})
        pkg = get_action(u'package_show')(context, {u'id': id})
    except NotFound:
        return base.abort(404, _(u'Resource not found'))
    except NotAuthorized:
        return base.abort(403, _(u'Not authorized to download resource'))
    

    if rsc.get(u'url_type') == u'upload':
        upload = uploader.get_resource_uploader(rsc)
        if MinioConnection().is_connected():

            filepath = upload.get_path_minio(pkg=pkg.get('name'), id=rsc[u'id'])
            filename = filename or rsc.get('name', 'downloaded_file')
        
            with urllib.request.urlopen(filepath) as response:
                file_data = response.read()
            
            response = Response(file_data)
            response.headers['Content-Disposition'] = f'attachment; file name = "{filename}"'
            response.headers['Content-Type'] = rsc.get('mimetype', 'application/octet-stream')
            return response
        else: 
            filepath = upload.get_path(rsc[u'id'])
            resp = flask.send_file(filepath, download_name=filename)
            if rsc.get('mimetype'):
                resp.headers['Content-Type'] = rsc['mimetype']
            signals.resource_download.send(resource_id)
            return resp
        
        

    elif u'url' not in rsc:
        return base.abort(404, _(u'No download is available'))
    return redirect(rsc['url'])

minio_download.add_url_rule(
    u'/<resource_id>/download/<filename>', view_func=download)


def get_blueprints():
    return [minio_download]
