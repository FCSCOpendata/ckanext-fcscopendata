import ckan.logic as logic
import ckan.model as model
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize
import logging

log = logging.getLogger(__name__)
def get_package_download_stats(package_id):
    context = {'model': model, 'session': model.Session}
    stats = logic.get_action('package_show')(context, {'id': package_id})
    return stats['total_downloads']

def get_dataset_group_list():
    context = {'model':model}
    q = model.Session.query(model.Group) \
        .filter(model.Group.is_organization == False) \
        .filter(model.Group.state == 'active')
    groups = q.all()
    group_list = model_dictize.group_list_dictize(groups, context)

    group_dropdown = [[group[u'id'], group[u'display_name']]
                          for group in group_list]

    return group_dropdown
  
def is_dataset_draft(package_id):
    context = {'model': model, 'session': model.Session}
    dataset = logic.get_action('package_show')(context, {'id': package_id})
    if dataset.get('publishing_status', '') == 'draft':
        return True
    else:
        return False
