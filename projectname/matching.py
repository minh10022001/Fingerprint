import numpy as np
import math
from itertools import combinations
from scipy.spatial import distance

def extract_angle(a: list, b: list) -> float:
    """
    Extract angle between two vectors with endpoints defined by two tuples.

    Args:
        a            (list): First segment that contains a starting coordinate (x, y) and an ending coordinate (x, y)
        b            (list): Second segment that contains a starting coordinate (x, y) and an ending coordinate (x, y)
        centre_angle (bool): True - free angle, False - constrained in the range [0, 180]

    Returns:
        float: Angle between the two segments.

    """

    # Vector form
    a_vec = [(a[0][0] - a[1][0]), (a[0][1] - a[1][1])]
    b_vec = [(b[0][0] - b[1][0]), (b[0][1] - b[1][1])]

    ab_dot = np.dot(a_vec, b_vec)
    a_mag = np.dot(a_vec, a_vec) ** 0.5
    b_mag = np.dot(b_vec, b_vec) ** 0.5

    # Radian angle to degrees
    angle = math.acos(round(ab_dot / (b_mag * a_mag), 6))

    angle_degrees = math.degrees(angle) % 360

    if angle_degrees - 180 >= 0:
        return 360 - angle_degrees
    else:
        return angle_degrees

def extract_tuple_profile(distances: list, m: tuple, minutiae: list, k: int) -> list:
    """
    Explores tuple profile. A tuple is a set of minutiae that are found close together.

    Args:
        distances (np.array): Distances between a tuple and its neighbours. Should be used for computing the tuple profile.
        m            (tuple): The base minutiae from which the distances are computed.
        minutiae      (list): List of tuple-like coordinates for all minutiae.

    Returns:
        list: [ratios, angles] - A pair of all angles (list) and all ratios (list) identified for the given tuple.

    """

    # Closest minutiae to the current minutiae
    closest_distances = sorted(distances)[1:k+1]
    closest_indices = [list(distances).index(d) for d in closest_distances]
    closest_minutiae = [minutiae[i] for i in closest_indices]

    # Unique pair ratios.
    # The 10 pairs used for computing the ratios
    # i-i1 : i-i2, i-i1 : i-i3, i-i1 : i-i4, i-i1 : i-i5,
    # i-i2 : i-i3, i-i2 : i-i4, i-i2 : i-i5
    # i-i3 : i-i4, i-i3 : i-i5
    # i-i4 : i-i5
    unique_pairs = list(combinations(closest_distances, 2))
    # 2 decimal rounded ratios of max of the two distances divided by their minimum.
    compute_ratios = [round(p[0]/p[1], 2) for p in unique_pairs]

    # Angle computation.
    minutiae_combinations = list(combinations(closest_minutiae, 2))

    # Angle between the segments drawn from m to the two other minutae with varying distances.
    minutiae_angles = [round(extract_angle((m, x), (m, y)), 2) for x, y in minutiae_combinations]

    return [compute_ratios, minutiae_angles]

def euclidian_distance(m1: tuple, m2: tuple) -> float:
    """
    Distance between 2 points based on their 2D coordinates

    Args:
        m1 (tuple): Coordinates (x, y) used as the first distance measurement point.
        m2 (tuple): Coordinates (x, y) used as the second distance measurement point.

    Returns:
        int: Distance between the two coordinates using euclidian distance (Pythagorean theorem)

    """

    return distance.euclidean(m1, m2)


# def generate_tuple_profile(minutiae: list, k:int) -> dict:
#     """
#     Compute the distance matrix from each minutiae to the rest.

#     Args:
#         minutiae (list): List of coordinate tuples.

#     Returns:
#         dict: Tuple profile with all angles and ratios.

#     """

#     distance_matrix = np.array([[euclidian_distance(i, j) for i in minutiae] for j in minutiae])

#     tuples = {}

#     for i, m in enumerate(minutiae):
#         # When comparing two tuple profiles, one from base and one from test image,
#         # they are the same if at least 2 ratios match (and angles).

#         # This means that for the tuple profile i is found in a second image under a
#         # different tuple's profile.

#         # Angles are given a +/- 3.5 degree range to match. To match sourcing device discrepancies.
#         ratios_angles = extract_tuple_profile(distance_matrix[i], m, minutiae ,k)
#         # tuples[m] = np.round(ratios_angles, 2)
#         tuples[str(m)] = ratios_angles

#     return tuples
def generate_tuple_profile(all_minutiae: list, each_minutiae: list, k:int) -> dict:
    distance_matrix = np.array([[euclidian_distance(i, j) for i in all_minutiae] for j in all_minutiae])

    tuples = {}

    for i, m in enumerate(all_minutiae):
        if m in each_minutiae:
            ratios_angles = extract_tuple_profile(distance_matrix[i], m, all_minutiae ,k)
            tuples[str(m)] = ratios_angles

    return tuples
# def match_tuples(tuple_base: dict, tuple_test: dict, th_range: float = .01, th_angle: float = 1.5):
#     """
#     Comparison between base and test tuples. 
#     Test ratios and angles as arrays.
#     Minutiae matching for computing similarity score between images. 

#     Args:
#         tuple_base (dict): Contains the base tuple coordinates as key with a nested list of ratios and angles with
#                             the closest 5 neighbours.
#         tuple_test (dict): Contains the test tuple coordinates as key with a nested list of ratios and angles with
#                             the closest 5 neighbours.
#         th_range  (float): Accepted matching threshold for the range criteria. Default: .01
#         th_angle  (float): Accepted matching threshold for the angle criteria. Default: 1.5

#     Returns:
#         list: confirmed matching tuples as a list of coordinates.

#     """

#     ratios_test = np.array([ratios for c, [ratios, _] in tuple_test.items()])
#     angles_test = np.array([angles for c, [_, angles] in tuple_test.items()])

#     common_points_base = []
#     common_points_test = []

#     # Tuple-wise comparison with all tuple profiles in the test image.
#     for i, (m, [ratios, angles]) in enumerate(tuple_base.items()):
#         # Explore matching ratios.
#         matching_values = (ratios_test == ratios).sum(1)

#         # Tuples found to match with this base tuple. 
#         matching_indices = np.where((matching_values == matching_values.max()) & (matching_values >= 2))[0]

#         if len(matching_indices) == 0:
#             continue
#         else:
#             matching_indices = matching_indices[0]

#         matching_ratios = ((ratios_test + th_range) >= ratios) * (ratios_test - th_range <= ratios)
#         matching_angles = ((angles_test + th_angle) >= angles) * (angles_test - th_angle <= angles)

#         matches = ((matching_ratios * ratios_test) * (matching_angles * angles_test) > 0).sum(1)

#         if matches.max() >= 6:
#             # Ratios and angles belonging to the current tuple are matched with 2 or
#             # more ratios and angles from another tuple from the test image. 
#             # This is a confirmed common point.
#             common_points_base.append(m)
#             common_points_test.append(list(tuple_test.keys())[matching_indices])

#     return common_points_base, common_points_test
    # return len(common_points_base)

def match_tuples(tuple_base: dict, tuple_test: dict, th_range: float = .01, th_angle: float = 1.5):
  
    ratios_test = np.array([ratios for c, [ratios, _] in tuple_test.items()])
    angles_test = np.array([angles for c, [_, angles] in tuple_test.items()])

    common_points_base = []
    common_points_test = []

    # Tuple-wise comparison with all tuple profiles in the test image.
    for i, (m, [ratios, angles]) in enumerate(tuple_base.items()):
       
        len_r = len(ratios)
        matching_ratios = ((ratios_test + th_range) >= ratios) * (ratios_test - th_range <= ratios)
        matching_angles = ((angles_test + th_angle) >= angles) * (angles_test - th_angle <= angles)

        matches = ((matching_ratios * ratios_test) * (matching_angles * angles_test) > 0).sum(1)
        matching_indices = np.where(matches == matches.max())[0]
       
        if len(matching_indices) ==0:
            continue
        elif matches.max() >= (len_r//2):
            # matching_indices = np.where(matches == matches.max())
            matching_indices = matching_indices[0]
            # print( matching_indices)
          
            # Ratios and angles belonging to the current tuple are matched with 2 or
            # more ratios and angles from another tuple from the test image. 
            # This is a confirmed common point.
            common_points_base.append(m)
            common_points_test.append(list(tuple_test.keys())[matching_indices])

    return common_points_base, common_points_test
def match(data_base: dict, data_test:dict, th_range: float = .01, th_angle: float = 1.5):
    termination_base = list(data_base.values())[0]
    bifurcation_base = list(data_base.values())[1]
    termination_test = list(data_test.values())[0]
    bifurcation_test = list(data_test.values())[1]

    common_points_base_t = []
    common_points_test_t = []
    common_points_base_b = []
    common_points_test_b = []

    if len(termination_base) >0 and len(termination_test)> 0:
        common_points_base_t , common_points_test_t = match_tuples(termination_base, termination_test, th_range, th_angle)
    
    if len(bifurcation_base)> 0 and len(bifurcation_test) > 0:
        common_points_base_b, common_points_test_b = match_tuples(bifurcation_base, bifurcation_test, th_range, th_angle)

    common_points_base = common_points_base_t +common_points_base_b
    common_points_test  = common_points_test_t + common_points_test_b

    return common_points_base, common_points_test
   
    
    



# def similarity_two_img(num_common_points: int, tuple_base: dict, tuple_test: dict ):
    
#     return num_common_points/((len( tuple_base)+len(tuple_test))/2)
def similarity_two_img(num_common_points, tuple_base, tuple_test):
    num_minutiae_base = len(tuple_base)
    num_minutiae_test = len(tuple_test)
    return num_common_points/((num_minutiae_base+num_minutiae_test)/2)