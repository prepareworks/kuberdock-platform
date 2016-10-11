from flask import Blueprint

from kubedock.api import check_api_version
from ..login import auth_required
from ..utils import KubeUtils, API_VERSIONS
from ..kapi.ippool import IpAddrPool
from ..rbac import check_permission


ippool = Blueprint('ippool', __name__, url_prefix='/ippool')


@ippool.route('/', methods=['GET'])
@ippool.route('/<path:network>', methods=['GET'])
@auth_required
@check_permission('get', 'ippool')
@KubeUtils.jsonwrap
def get_ippool(network=None):
    params = KubeUtils._get_params()
    if 'free-only' in params:
        return IpAddrPool.get_free()
    if check_api_version([API_VERSIONS.v2]):
        if network:
            return IpAddrPool.get_network_ips(network)
        else:
            return IpAddrPool.get_networks_list()
    page = int(params.get('page', 1))
    return IpAddrPool.get(network, page)


# @ippool.route('/getFreeHost', methods=['GET'])
# @auth_required
# @KubeUtils.jsonwrap
# def get_free_address():
#     return IpAddrPool().get_free()


@ippool.route('/userstat', methods=['GET'])
@auth_required
@KubeUtils.jsonwrap
def get_user_address():
    user = KubeUtils.get_current_user()
    return IpAddrPool.get_user_addresses(user)


@ippool.route('/', methods=['POST'])
@auth_required
@check_permission('create', 'ippool')
@KubeUtils.jsonwrap
def create_item():
    params = KubeUtils._get_params()
    pool = IpAddrPool.create(params)

    if check_api_version([API_VERSIONS.v2]):
        return IpAddrPool.get_network_ips(params['network'])
    return pool.to_dict(page=1)


@ippool.route('/<path:network>', methods=['PUT'])
@auth_required
@check_permission('edit', 'ippool')
@KubeUtils.jsonwrap
def update_ippool(network):
    params = KubeUtils._get_params()
    net = IpAddrPool.update(network, params)
    if check_api_version([API_VERSIONS.v2]):
        return IpAddrPool.get_network_ips(network)
    return net.to_dict()


@ippool.route('/<path:network>', methods=['DELETE'])
@auth_required
@check_permission('delete', 'ippool')
@KubeUtils.jsonwrap
def delete_ippool(network):
    return IpAddrPool.delete(network)


@ippool.route('/get-public-ip/<path:node>/<path:pod>', methods=['GET'])
@auth_required
@KubeUtils.jsonwrap
def get_public_ip(node, pod):
    return IpAddrPool.assign_ip_to_pod(pod, node)


@ippool.route('/mode', methods=['GET'])
@auth_required
@KubeUtils.jsonwrap
def get_mode():
    return IpAddrPool.get_mode()
