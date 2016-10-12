import yaml

from flask import Blueprint, Response
from flask.views import MethodView

from kubedock.api.utils import use_kwargs
from kubedock.decorators import maintenance_protected
from kubedock.exceptions import APIError, InsufficientData, PredefinedAppExc
from kubedock.kapi.apps import PredefinedApp, start_pod_from_yaml
from kubedock.kapi.podcollection import PodCollection
from kubedock.login import auth_required
from kubedock.rbac import check_permission
from kubedock.utils import KubeUtils, register_api, send_event_to_user
from kubedock.validation.coerce import extbool


yamlapi = Blueprint('yaml_api', __name__, url_prefix='/yamlapi')


class YamlAPI(KubeUtils, MethodView):
    decorators = (
        KubeUtils.jsonwrap,
        check_permission('create', 'yaml_pods'),
        KubeUtils.pod_start_permissions,
        auth_required
    )

    @maintenance_protected
    @use_kwargs({'data': {'type': 'string', 'empty': False}},
                allow_unknown=True)
    def post(self, **params):
        user = self.get_current_user()
        data = params.get('data')
        if data is None:
            raise InsufficientData('No "data" provided')
        try:
            parsed_data = list(yaml.safe_load_all(data))
        except yaml.YAMLError as e:
            raise PredefinedAppExc.UnparseableTemplate(
                'Incorrect yaml, parsing failed: "{0}"'.format(str(e)))

        try:
            res = start_pod_from_yaml(parsed_data, user=user)
        except APIError as e:  # pass as is
            raise
        except Exception as e:
            raise PredefinedAppExc.InternalPredefinedAppError(
                details={'message': str(e)})
        send_event_to_user('pod:change', res, user.id)
        return res

register_api(yamlapi, YamlAPI, 'yamlapi', '/', 'pod_id')


@yamlapi.route('/fill/<int:template_id>/<int:plan_id>', methods=['POST'])
@use_kwargs({}, allow_unknown=True)
def fill_template(template_id, plan_id, **params):
    app = PredefinedApp.get(template_id)
    filled = app.get_filled_template_for_plan(plan_id, params, as_yaml=True)
    return Response(filled, content_type='application/x-yaml')


@yamlapi.route('/create/<int:template_id>/<int:plan_id>', methods=['POST'])
@auth_required
@check_permission('create', 'yaml_pods')
@KubeUtils.jsonwrap
@use_kwargs({'start': {'type': 'boolean', 'coerce': extbool}},
            allow_unknown=True)
def create_pod(template_id, plan_id, **data):
    user = KubeUtils.get_current_user()
    start = data.pop('start', True)

    app = PredefinedApp.get(template_id)
    pod_data = app.get_filled_template_for_plan(plan_id, data, user=user)
    res = start_pod_from_yaml(pod_data, user=user, template_id=template_id)
    if start:
        PodCollection(user).update(res['id'],
                                   {'command': 'start', 'commandOptions': {}})
    return res


@yamlapi.route('/switch/<pod_id>/<plan_id>', methods=['PUT'])
@auth_required
@KubeUtils.jsonwrap
@use_kwargs({'async': {'type': 'boolean', 'coerce': extbool},
             'dry-run': {'type': 'boolean', 'coerce': extbool}},
            allow_unknown=True)
def switch_pod_plan(pod_id, plan_id, **params):
    async = params.get('async', True)
    dry_run = params.get('dry-run', False)
    current_user = KubeUtils.get_current_user()
    if plan_id.isdigit():   # plan_id specified with index (e.g. 0)
        plan_id = int(plan_id)
        func = PredefinedApp.update_pod_to_plan
    else:  # plan_id specified with name ('M', 'XXL')
        func = PredefinedApp.update_pod_to_plan_by_name
    return func(pod_id, plan_id,
                async=async, dry_run=dry_run, user=current_user)
