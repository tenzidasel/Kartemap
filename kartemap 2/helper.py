import math


def compute_distance_in_kilometers(lon1, lat1, lon2, lat2):
    """
    Uses the ‘haversine’ formula to calculate the great-circle distance between
    two points on the earth’s surface – giving an ‘as-the-crow-flies’ distance between the
    points.
    """
    phi_1 = lat1 * math.pi / 180.0
    phi_2 = lat2 * math.pi / 180.0
    change_phi = (lat2 - lat1) * math.pi / 180
    change_lambda = (lon2 - lon1) * math.pi / 180

    a = math.sin(change_phi / 2.0) * math.sin(change_phi / 2.0) + math.cos(phi_1) * \
        math.cos(phi_2) * math.sin(change_lambda / 2.0) * math.sin(change_lambda / 2.0)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return 6371.0 * c


def compute_distance_in_miles(lon1, lat1, lon2, lat2):
    """
    Uses the ‘haversine’ formula to calculate the great-circle distance between
    two points on the earth’s surface – giving an ‘as-the-crow-flies’ distance between the
    points.
    """
    return compute_distance_in_kilometers(lon1, lat1, lon2, lat2) / 1.60934
