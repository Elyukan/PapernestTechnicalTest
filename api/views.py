from typing import Any
from adrf.views import APIView
from django.http import JsonResponse
from django.conf import settings
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.request import Request

from .models import NetworkProviderTowerModel
import re

from .serializers import NetworkCoverageSerializer
import asyncio
import httpx

class NetworkCoverageView(APIView):
    serializer_class = NetworkCoverageSerializer

    async def fetch_data(self, network_provider_towers: list[NetworkProviderTowerModel], address: tuple[str, str, str]) -> dict:
        """
        Method that fetches the network coverage of a given address for each network provider
        """
        response_data: dict = {}

        async with httpx.AsyncClient() as client:
            # Calling the gouvernment API to find the best possible match for the given address
            response = await client.get(settings.API_ADDRESS_GOUV_URL, params={"q": address[1]})
            data: dict = response.json()

            # If no match is found we are returning / logging an error.
            if len(data["features"]) == 0:
                print(data["features"])
                return {
                    address[0]: {"Error": "Adresse invalide ou introuvable. Aucune correspondance trouvé."}
                }
            
            # If at least one match is found, we are checking if the matching score is acceptable.
            # If none match meets the threshold, so we are returning / logging an error.
            is_match = False
            for elem in data["features"]:
                if elem["properties"]["score"] >= settings.MIN_MATCH_SCORE:
                    is_match = True
                    x_coordinate = int(elem["properties"]["x"])
                    y_coordinate = int(elem["properties"]["y"])
                    break
            if not is_match:
                return {
                    address[0]: {"Error": f"Adresse invalide ou introuvable. {len(data['features'])} correspondance(s) trouvé(s) mais aucune ne correspond parfaitement."}
                }
        
        # We loop through our previously "postcode-filtered" towers, calculate the distance between the address and the towers and determine if the address is in the coverage area
        for tower in network_provider_towers:
            coverage_data = await tower.get_coverage_from_coordinate(x_coordinate, y_coordinate)

            # A tower may be too far away to be in range, but another one might, so we are updating the dict accordingly
            if tower.network_provider.name not in response_data:
                response_data[tower.network_provider.name] = coverage_data
            else:
                response_data[tower.network_provider.name]["2G"] = any([response_data[tower.network_provider.name]["2G"], coverage_data["2G"]])
                response_data[tower.network_provider.name]["3G"] = any([response_data[tower.network_provider.name]["3G"], coverage_data["3G"]])
                response_data[tower.network_provider.name]["4G"] = any([response_data[tower.network_provider.name]["4G"], coverage_data["4G"]])
        return {
            address[0]: response_data
        }

    async def post(self, request: Request, *args: Any, **kwargs: Any):
        """
        Post request which returns the coverage of the addresses given in the body
        """
        pattern = r"([^,]+),?\s*(\d{5})\s([A-Za-zÀ-ÖØ-öø-ÿ\s'-]+)$" # Regex that matchs with an address
        postalcodes: list[str] = []
        addresses: list[tuple[str, str, str]] = []
        network_provider_towers_regarding_postcode: dict = {}

        # Validate the request body format
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # We loop through the addresses to extract the required data.
        for address in serializer.validated_data["addresses"]:
            try:
                match = re.search(pattern, address["address"])
                adresse_complete = address["address"].strip()
                code_postal = match.group(2)
                postalcodes.append(code_postal)
                addresses.append((address["identifier"], adresse_complete, code_postal))
            except AttributeError:
                # If an address is wrongly formated, return an error
                return JsonResponse({"Status": "Error", "message": f"{address['address']} - Adresse mal formatée"}, status=HTTP_400_BAD_REQUEST)

        # The request only fetch instances that matchs with the given postal codes to prevent unnecessary database queries.
        queryset = NetworkProviderTowerModel.objects.filter(postcode__in=postalcodes).select_related("network_provider")

        # To avoid redundant database queries, we structure the result in a dictionary.
        # This optimizes performance by filtering instances once and preventing O(n^2) complexity.
        async for instance in queryset:
            if instance.postcode not in network_provider_towers_regarding_postcode:
                network_provider_towers_regarding_postcode[instance.postcode] = []
            network_provider_towers_regarding_postcode[instance.postcode].append(instance)
        
        # each task fetches coverage for an address in particular using only the towers that match with the postcode (to prevent over-fetching)
        tasks = [self.fetch_data(network_provider_towers_regarding_postcode[address[2]], address) for address in addresses]
        results = await asyncio.gather(*tasks)

        # Merge all results into a single response.
        final_response = {}
        for result in results:
            final_response.update(result)
        
        return JsonResponse(final_response)
