from .extras import dict_to_object, object_to_dict
from .simple_rpc import Interface, SerialInterface, SocketInterface


def _get_metadata(name: str) -> str:
    defaults = {
        'Name': 'arduino-simple-rpc',
        'Version': '2.4.2',
        'Summary': 'Arduino simpleRPC API client library and CLI.',
        'Author': 'Jeroen F.J. Laros',
        'Author-email': 'jlaros@fixedpoint.nl',
        'Home-page': 'https://arduino-simple-rpc.readthedocs.io',
    }
    try:
        from importlib.metadata import metadata
        return str(metadata('arduino-simple-rpc').get(name) or defaults.get(name, ''))
    except Exception:
        return defaults.get(name, '')


_copyright_notice = 'Copyright (c) {} <{}>'.format(
    _get_metadata('Author'), _get_metadata('Author-email'))

usage = [_get_metadata('Summary'), _copyright_notice]


def doc_split(func: callable) -> str:
    return func.__doc__.split('\n\n')[0]


def version(name: str) -> str:
    return '{} version {}\n\n{}\nHomepage: {}'.format(
        _get_metadata('Name'), _get_metadata('Version'), _copyright_notice,
        _get_metadata('Home-page'))
