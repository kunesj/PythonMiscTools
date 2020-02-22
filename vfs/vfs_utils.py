#!/usr/bin/python3
# coding: utf-8

import os
import urllib.parse
from typing import Union


def parse_uri(uri: Union[str, None], unquote: bool = False) -> dict:
    obj = urllib.parse.urlparse(uri)
    data = {
        'scheme': obj.scheme,
        'netloc': obj.netloc,
        'path': obj.path,
        'params': obj.params,
        'query': obj.query,
        'fragment': obj.fragment,
    }
    data = {k: data[k].decode('utf-8') if isinstance(data[k], bytes) else data[k] for k in data}
    if unquote:
        data = {k: urllib.parse.unquote(data[k]) for k in data}
    return data


def convert_uri_to_fs_path(uri: Union[str, None]) -> Union[str, None]:
    uri_p = parse_uri(uri, unquote=True)

    # detect if is filesystem path
    if uri_p['scheme'] not in ['file', '']:
        return None
    if not (uri_p['netloc']+uri_p['path']).strip():
        return None

    # make sure that '~' and '/some/path' join correctly
    if uri_p['netloc'] == '~':
        uri_p['netloc'] = os.path.expanduser(uri_p['netloc'])
        if uri_p['path'].startswith('/'):
            uri_p['path'] = uri_p['path'][1:]

    # join and turn into abs path
    path = os.path.abspath(os.path.join(uri_p['netloc'], uri_p['path']))

    return path


def parse_file_type(file_name):
    """
    :return: Lowercase extension or None
    """
    file_type = os.path.splitext(file_name)[1].lower()
    if file_type.startswith('.'):
        file_type = file_type[1:]
    if file_type == '':
        file_type = None
    return file_type
