from email.policy import default
import ckan.logic as logic
import ckan.model as model
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize
import logging
from ckan.common import config
import distutils.util
from urllib.parse import urlparse
from ckan.lib.helpers import build_nav_main, _make_menu_item, literal

log = logging.getLogger(__name__)

def get_package_download_stats(package_id):
    context = {'model': model, 'session': model.Session}
    stats = logic.get_action('package_show')(context, {'id': package_id})
    return stats['total_downloads']

def is_dataset_draft(package_id):
    context = {'model': model, 'session': model.Session}
    dataset = logic.get_action('package_show')(context, {'id': package_id})
    if dataset.get('publishing_status', '') == 'draft':
        return True
    else:
        return False


def get_dataset_group_list(pkg_dict):
    context = {'model':model}
    q = model.Session.query(model.Group) \
        .filter(model.Group.is_organization == False) \
        .filter(model.Group.state == 'active')
    groups = q.all()
    group_list = model_dictize.group_list_dictize(groups, context)
    if pkg_dict['groups']:
        for group in pkg_dict['groups']:
            for group_element in group_list:
                if group_element['id'] == group['id']:
                    group_list.remove(group_element)

    group_dropdown = [[group[u'id'], group[u'display_name']]
                          for group in group_list]

    return group_dropdown


def get_cms_url():
    default = 'https://cms.fcsc.production.datopian.com/ghost'
    key = 'ckanext.fcsc.cms'
    if config.get(key):
        url = config.get(key)
        if bool(urlparse(url).netloc):
            return url
        return default
    else:
        return default


def build_nav_main(*args):
    ''' build a set of menu items.

    args: tuples of (menu type, title) eg ('login', _('Login'))
    outputs <li><a href="...">title</a></li>
    '''
    output = ''
    for item in args:
        menu_item, title = item[:2]
        if len(item) == 3 and not check_access(item[2]):
            continue
        
        if title == "About":
            link = literal(f'<li><a href={get_cms_url()} target="_blank" rel="noopener noreferrer">CMS Admin</a></li>')
            output += link
            output += _make_menu_item(menu_item, title)
        else:
            output += _make_menu_item(menu_item, title)
    return output