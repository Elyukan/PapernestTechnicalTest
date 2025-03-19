import pytest
from asgiref.sync import async_to_sync
from .models import NetworkProviderModel, NetworkProviderTowerModel

@pytest.fixture
def build_provider():
    def build_provider(name):
        return NetworkProviderModel.objects.create(name=name)
    return build_provider

@pytest.fixture
def build_tower():
    def build_tower(postcode, x, y, network_provider, is_2G=True, is_3G=True, is_4G=True):
        return NetworkProviderTowerModel.objects.create(network_provider=network_provider, postcode=postcode, x_coordinate=x, y_coordinate=y, is_2G=is_2G, is_3G=is_3G, is_4G=is_4G)
    return build_tower

@pytest.mark.django_db
class TestCoverage:
    def test_get_coverage_from_coordinate(
        self,
        build_tower,
        build_provider
    ):
        network_provider = build_provider(name="SFR")
        tower = build_tower("75019", 653735, 6865655, network_provider) # Near from the address
        x = 654412
        y = 6866689
        result = async_to_sync(tower.get_coverage_from_coordinate)(x, y)
        assert result["2G"] is True
        assert result["3G"] is True
        assert result["4G"] is True

    def test_get_coverage_from_coordinate_not_in_range(
        self,
        build_tower,
        build_provider
    ):
        network_provider = build_provider(name="Orange")
        tower = build_tower("75016", 644437, 6861202, network_provider) # Far from the address
        x = 654412
        y = 6866689
        result = async_to_sync(tower.get_coverage_from_coordinate)(x, y)
        assert result["2G"] is True
        assert result["3G"] is False
        assert result["4G"] is False
