import ckan.model as model
from ckan.common import _, g, request
import ckan.plugins.toolkit as tk
from ckan.views.api import _finish_ok
from ckan.views.dataset import GroupView

def vocab_tag_autocomplete():
    q = request.args.get(u'incomplete', u'')
    context = {u'model': model, u'session': model.Session,
                   u'user': g.user, u'auth_user_obj': g.userobj}

    limit = request.args.get(u'limit', 10)
    vocab_list = tk.get_action(u'vocabulary_list')(context, {})

    tag_list = []
    if q:
        data_dict = {u'q': q, u'limit': limit}

        for vocab in vocab_list:
            tags = tk.get_action(u'tag_autocomplete')(context, 
                {**data_dict,'vocabulary_id': vocab['id'] })
            for tag_item in tags:
                tag_list.append(tag_item) 
            
    resultSet = {
        u'ResultSet': {
            u'Result': [{u'Name': tag} for tag in tag_list]
        }
    }

    return _finish_ok(resultSet)

class GroupManage(GroupView):
    def post(self, package_type, id):
        context, pkg_dict = self._prepare(id)
        new_group = request.form.get(u'group_added')

        try:
            tk.check_access('package_update', context, pkg_dict)
        except tk.NotFound:
            tk.abort(404, _('Dataset not found'))
        except tk.NotAuthorized:
            tk.abort(403, _('User %r not authorized to manage themes'))

        if new_group:
            data_dict = {
                u"id": new_group,
                u"object": id,
                u"object_type": u'package',
                u"capacity": u'public'
            }
            try:
                tk.get_action(u'member_create')(dict(context, ignore_auth=True), data_dict)
            except tk.NotFound:
                return tk.abort(404, _(u'Group not found'))

        removed_group = None
        for param in request.form:
            if param.startswith(u'group_remove'):
                removed_group = param.split(u'.')[-1]
                break
        if removed_group:
            data_dict = {
                u"id": removed_group,
                u"object": id,
                u"object_type": u'package'
            }
            try:
                tk.get_action(u'member_delete')(dict(context, ignore_auth=True), data_dict)
            except tk.NotFound:
                return tk.abort(404, _(u'Group not found'))
        return tk.h.redirect_to(u'{}.groups'.format(package_type), id=id)