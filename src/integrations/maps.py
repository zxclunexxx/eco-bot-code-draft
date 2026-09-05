from urllib.parse import quote


def google_maps_route_url(destination_lat: float, destination_lon: float, user_lat: float | None = None, user_lon: float | None = None) -> str:
    if user_lat is not None and user_lon is not None:
        return (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={user_lat},{user_lon}&destination={destination_lat},{destination_lon}"
        )
    return f"https://www.google.com/maps/search/?api=1&query={destination_lat},{destination_lon}"


def yandex_maps_route_url(destination_lat: float, destination_lon: float, user_lat: float | None = None, user_lon: float | None = None) -> str:
    if user_lat is not None and user_lon is not None:
        return f"https://yandex.ru/maps/?rtext={user_lat},{user_lon}~{destination_lat},{destination_lon}&rtt=auto"
    return f"https://yandex.ru/maps/?ll={destination_lon},{destination_lat}&z=16"
