from email.policy import default
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import json
from ckanext.fcscopendata.logic import action
import ckanext.fcscopendata.cli as cli
from ckanext.fcscopendata.views import vocab_tag_autocomplete, GroupManage
from ckanext.fcscopendata.helpers import get_package_download_stats, get_dataset_group_list

from ckan.lib.plugins import DefaultTranslation

from flask import Blueprint, render_template

def hello_plugin():
    return u'Hello from the fcscopendata Theme extension'


class FcscopendataPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.ITemplateHelpers)


    # IPackageController
    def before_index(self, pkg_dict):
        # Index vocab tags as tag field also so that
        # it is searchable via default tag query.
        data_dict = json.loads(pkg_dict.get('data_dict', {}))
        if data_dict.get('tags', []):
            tag_list = []
            tags = data_dict.get('tags', [])
            for tag in tags:
                tag_list.append(tag['name'])
            pkg_dict['tags'] = tag_list
        return pkg_dict

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets',
                             'fcscopendata')

    # IBlueprint
    def get_blueprint(self):
        u'''Return a Flask Blueprint object to be registered by the app.'''
        # Create Blueprint for plugin
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'
        # Add plugin url rules to Blueprint object
        blueprint.add_url_rule(u'/api/2/util/vocab/tag/autocomplete', methods=[u'GET'], 
                                view_func=vocab_tag_autocomplete)
        blueprint.add_url_rule(u'/dataset/groups/<id>', defaults= {u'package_type': u'dataset'},
                                view_func=GroupManage.as_view(str(u'groups')))
        return blueprint

    def get_actions(self):
        return action.get_actions()

    # IClick
    def get_commands(self):
        return cli.get_commands()


    #ITemplateHelpers
    def get_helpers(self):
        return {
            'get_package_download_stats': get_package_download_stats,
            'get_dataset_group_list': get_dataset_group_list
        }
