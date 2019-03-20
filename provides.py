import base64
from charms.reactive import Endpoint


class PacemakerRemoteProvides(Endpoint):

    def publish_info(self, remote_hostname, stonith_hostname=None,
                     enable_resources=True):
        """
        Publish the stonith info
        """
        for relation in self.relations:
            relation.to_publish['stonith-hostname'] = stonith_hostname
            relation.to_publish['remote-hostname'] = remote_hostname
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
