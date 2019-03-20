import unittest
import mock


with mock.patch('charmhelpers.core.hookenv.metadata') as _meta:
    _meta.return_Value = 'ss'
    import provides


_hook_args = {}

TO_PATCH = [
]


def mock_hook(*args, **kwargs):

    def inner(f):
        # remember what we were passed.  Note that we can't actually determine
        # the class we're attached to, as the decorator only gets the function.
        _hook_args[f.__name__] = dict(args=args, kwargs=kwargs)
        return f
    return inner


class _unit_mock:
    def __init__(self, unit_name, received=None):
        self.unit_name = unit_name
        self.received = received or {}


class _relation_mock:
    def __init__(self, application_name=None, units=None):
        self.to_publish_raw = {}
        self.to_publish = {}
        self.application_name = application_name
        self.units = units


class TestPacemakerRemoteProvides(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._patched_hook = mock.patch('charms.reactive.when', mock_hook)
        cls._patched_hook_started = cls._patched_hook.start()
        # force provides to rerun the mock_hook decorator:
        # try except is Python2/Python3 compatibility as Python3 has moved
        # reload to importlib.
        try:
            reload(provides)
        except NameError:
            import importlib
            importlib.reload(provides)

    @classmethod
    def tearDownClass(cls):
        cls._patched_hook.stop()
        cls._patched_hook_started = None
        cls._patched_hook = None
        # and fix any breakage we did to the module
        try:
            reload(provides)
        except NameError:
            import importlib
            importlib.reload(provides)

    def patch(self, method):
        _m = mock.patch.object(self.obj, method)
        _mock = _m.start()
        self.addCleanup(_m.stop)
        return _mock

    def setUp(self):
        self.relation_obj = provides.PacemakerRemoteProvides(
            'some-relation',
            [])
        self._patches = {}
        self._patches_start = {}
        self.obj = provides
        for method in TO_PATCH:
            setattr(self, method, self.patch(method))

    def tearDown(self):
        self.relation_obj = None
        for k, v in self._patches.items():
            v.stop()
            setattr(self, k, None)
        self._patches = None
        self._patches_start = None

    def patch_relation_obj(self, attr, return_value=None):
        mocked = mock.patch.object(self.relation_obj, attr)
        self._patches[attr] = mocked
        started = mocked.start()
        started.return_value = return_value
        self._patches_start[attr] = started
        setattr(self, attr, started)

    def test_publish_info(self):
        mock_rel = _relation_mock()
        self.relation_obj._relations = [mock_rel]
        self.relation_obj.publish_info(
            'node1.az1.local',
            stonith_hostname='node1.stonith',
            enable_resources=True)
        expect = {
            'remote-hostname': 'node1.az1.local',
            'stonith-hostname': 'node1.stonith',
            'enable-resources': True}
        self.assertEqual(
            mock_rel.to_publish,
            expect)

    def test_get_pacemaker_key(self):
        unit1 = _unit_mock(
            'unit1',
            received={'pacemaker-key': 'cG1ha2Vya2V5MQo='})
        mock_rel = _relation_mock(units=[unit1])
        self.relation_obj._relations = [mock_rel]
        self.assertEqual(
            self.relation_obj.get_pacemaker_key(),
            b'pmakerkey1\n')

    def test_get_pacemaker_key_inconsistent(self):
        unit1 = _unit_mock(
            'unit1',
            received={'pacemaker-key': 'cG1ha2Vya2V5MQo='})
        unit2 = _unit_mock(
            'unit2',
            received={'pacemaker-key': 'cG1ha2Vya2V5Mgo='})
        mock_rel = _relation_mock(units=[unit1, unit2])
        self.relation_obj._relations = [mock_rel]
        with self.assertRaises(Exception):
            self.relation_obj.get_pacemaker_key()

    def test_get_pacemaker_key_missing(self):
        unit1 = _unit_mock(
            'unit1',
            received={})
        unit2 = _unit_mock(
            'unit2',
            received={})
        mock_rel = _relation_mock(units=[unit1, unit2])
        self.relation_obj._relations = [mock_rel]
        self.assertEqual(
            self.relation_obj.get_pacemaker_key(),
            None)
