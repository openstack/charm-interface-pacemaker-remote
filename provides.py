import base64
from charms.reactive import Endpoint


class PacemakerRemoteProvides(Endpoint):

    def publish_info(self, remote_hostname, remote_ip, stonith_hostname=None,
                     enable_resources=True):
        """Publish the stonith info.


       :param remote_hostname: The hostname of this unit
       :type remote_hostname: str
       :param remote_ip: The IP address that the c;uster should contanct this
                         node on.
       :type remote_ip: str
       :param stonith_hostname: The name used by the stonith device to refer
                                to this node.
       :type stonith_hostname: str
       :param enable_resources: Whether this node should run resources from
                                the cluster.
       :type enable_resources: bool
        """
        for relation in self.relations:
            relation.to_publish['stonith-hostname'] = stonith_hostname
            relation.to_publish['remote-hostname'] = remote_hostname
            relation.to_publish['remote-ip'] = remote_ip
            relation.to_publish['enable-resources'] = enable_resources

    def get_pacemaker_key(self):
        for relation in self.relations:
            pacemaker_keys = []
            for unit in relation.units:
                key = unit.received.get('pacemaker-key')
                if key:
                    pacemaker_keys.append(key)
            unique_keys = len(set(pacemaker_keys))
            if unique_keys > 1:
                raise Exception("Inconsistent keys")
            elif unique_keys == 1:
                return base64.b64decode(pacemaker_keys[0])
        return None
