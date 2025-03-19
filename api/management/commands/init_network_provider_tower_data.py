import io
import csv
import requests

from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from pyproj import Transformer
from typing import Any

from api.models import NetworkProviderModel, NetworkProviderTowerModel


CHUNK_SIZE = 10000

class Command(BaseCommand):
    help = "Command that initializes network provider towers in the database from a csv provided as a parameter"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--path", type=str, help="path to csv file", required=True)

    def lamber93_to_gps(self, x: int, y: int) -> tuple[float, float]:
        """
        Method that convert Lambert93 coordinates into latitude and longitude coordinates
        """
        transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
        lon: float
        lat: float
        lon, lat = transformer.transform(x, y)
        return lon, lat
    
    def send_partial_csv(self, output_buffer: io.StringIO) -> None:
        """
        Method that takes buffer as a parameter, sends it to the gouvernment API and creates the network provider towers.
        """
        output_buffer.seek(0)
        files = {"data": ("partial_csv.csv", output_buffer.getvalue(), "text/csv")}
        url = "https://data.geopf.fr/geocodage/reverse/csv/"
        response = requests.post(url, files=files)
        result_buffer = io.StringIO(response.text)
        csv_reader = csv.reader(result_buffer)
        headers = next(csv_reader)

        x_coordinate_index = headers.index("x")
        y_coordinate_index = headers.index("y")
        operateur_index = headers.index("Operateur")
        _2G_index = headers.index("2G")
        _3G_index = headers.index("3G")
        _4G_index = headers.index("4G")
        postcode_index = headers.index("result_postcode")

        for row in csv_reader:
            operateur_name = row[operateur_index]
            x_coordinate = row[x_coordinate_index]
            y_coordinate = row[y_coordinate_index]
            is_2G = row[_2G_index]
            is_3G = row[_3G_index]
            is_4G = row[_4G_index]
            postcode = row[postcode_index]
            if operateur_name not in self.network_providers_regarding_name:
                # We create the network providers instances dynamically as we encounter them for the first time
                self.network_providers_regarding_name[operateur_name] = NetworkProviderModel.objects.create(name=operateur_name)
            # Store them in a dictionary to minimize database queries
            operateur = self.network_providers_regarding_name[operateur_name]
            # We store the postcode of the cities where the towers takes place
            # Instances will be created in batch at the end for optimization
            self.network_provider_towers.append(NetworkProviderTowerModel(network_provider=operateur, x_coordinate=x_coordinate, y_coordinate=y_coordinate, is_2G=is_2G, is_3G=is_3G, is_4G=is_4G, postcode=postcode))

    def handle(self, path: str, *args: Any, **options: Any) -> None:
        """
        Entrypoint of the manage command
        """
        # The gouvernment API has an endpoint that allows reverse geocoding from coordinates by sending them in a CSV file.
        # Because we are dealing with large csv files and want to avoid excessive API calls, we use the CSV-based API call.
        self.network_provider_towers: list[NetworkProviderTowerModel] = []
        self.network_providers_regarding_name: dict[str, NetworkProviderModel] = {}
        with open(path, "r") as f:
            content = f.read()
        buffer = io.StringIO(content)
        output_buffer = io.StringIO()
        csv_reader = csv.reader(buffer)
        csv_writer = csv.writer(output_buffer)

        headers = next(csv_reader) + ["lat", "lon"]
        csv_writer.writerow(headers)

        x_coordinate_index = headers.index("x")
        y_coordinate_index = headers.index("y")
        count = 0
        # The main issue here is handling large csv files which can contain than 50k lines.
        # To manage this, we divide the data into smaller chunks before sending them to the government API.
        for row in csv_reader:
            # The reverse geocoding API only handles latitude and longitude coordinates,
            # so we need to convert the Lambert93 coordinates and add them to the in-memory CSV.
            lon, lat = self.lamber93_to_gps(int(row[x_coordinate_index]), int(row[y_coordinate_index]))
            row += [str(lat), str(lon)]
            csv_writer.writerow(row)
            count += 1

            # When the chunk is full we send it to the API and process the response to create our network provider towers
            if count % CHUNK_SIZE == 0:
                self.send_partial_csv(output_buffer)
                # Reset the buffer
                output_buffer = io.StringIO()
                csv_writer = csv.writer(output_buffer)
                csv_writer.writerow(headers)

        # Send the remaining data in the CSV file
        if count % CHUNK_SIZE != 0:
            self.send_partial_csv(output_buffer)
        
        # Insert all instances into the database using bulk_create to optimize database performance
        NetworkProviderTowerModel.objects.bulk_create(self.network_provider_towers, batch_size=CHUNK_SIZE)


        

