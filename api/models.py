import math
from django.db import models
from django.conf import settings


class NetworkProviderModel(models.Model):
    """
    Model that represent the network providers instances in the database
    """
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class NetworkProviderTowerModel(models.Model):
    """
    Model that represent the network provider towers instances in the database
    """
    network_provider = models.ForeignKey(NetworkProviderModel, on_delete=models.CASCADE, related_name="towers")
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    postcode = models.CharField(max_length=5)
    is_2G = models.BooleanField()
    is_3G = models.BooleanField()
    is_4G = models.BooleanField()

    def __str__(self) -> str:
        return f"{self.network_provider} tower in {self.postcode} ({self.x_coordinate},{self.y_coordinate})"
    
    async def get_coverage_from_coordinate(self, x: int, y: int) -> dict:
        """
        Method that takes the lambert93 coordinates of the address in parameters,
        calculate the distance between the tower and the address, check if the address is in the coverage area
        and then returns the result as a dict
        """
        distance_km = math.sqrt((self.x_coordinate - x)**2 + (self.y_coordinate - y)**2) / 1000
        return {
            "2G": distance_km <= settings.DISTANCE_COVERAGE_2G,
            "3G": distance_km <= settings.DISTANCE_COVERAGE_3G,
            "4G": distance_km <= settings.DISTANCE_COVERAGE_4G,
        }
