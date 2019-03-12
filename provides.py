import base64
from charms.reactive import Endpoint


class PacemakerProvides(Endpoint):

    def publish_info(self, stonith_hostname=None):
        """
        Publish the stonith info
        """
        for relation in self.relations:
            relation.to_publish['stonith-hostname'] = stonith_hostname

    def get_pacemaker_key(self):
        for relation in self.relations:
            pacemaker_keys = []
            for unit in relation.units:
                pacemaker_keys.append(unit.received['pacemaker-key'])
            unique_keys = len(set(pacemaker_keys))
            if unique_keys > 1:
                raise Exception("Inconsistent keys")
            elif unique_keys == 1:
                return base64.decode(unique_keys[0])
        return None
