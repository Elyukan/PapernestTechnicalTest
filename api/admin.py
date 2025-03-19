from django.contrib import admin
from .models import NetworkProviderModel, NetworkProviderTowerModel

@admin.register(NetworkProviderModel)
class NetworkProviderAdmin(admin.ModelAdmin):
    pass


@admin.register(NetworkProviderTowerModel)
class NetworkProviderTowerAdmin(admin.ModelAdmin):
    list_display = ("id", "network_provider", "x_coordinate", "y_coordinate", "postcode", "is_2G", "is_3G", "is_4G")

    search_fields = ("postcode",)
    
    list_filter = ("network_provider", "is_2G", "is_3G", "is_4G")