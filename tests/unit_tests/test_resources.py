import chalicelib.resources as resources
from tests.unit_tests.fixtures.resources_fixtures import mock_env_variable


def test_resources(mock_env_variable):
    resources_obj = resources.Resources()
    assert resources_obj.logging_level == "INFO"
    assert isinstance(resources_obj.get_default_url, str)
