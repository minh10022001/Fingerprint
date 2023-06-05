
from ast import Break
from tabnanny import check
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

def generate_tuple_profile(all_minutiae: list, each_minutiae: list, k:int) -> dict:
    distance_matrix = np.array([[euclidian_distance(i, j) for i in all_minutiae] for j in all_minutiae])

    tuples = {}

    for i, m in enumerate(all_minutiae):
        if m in each_minutiae:
            ratios_angles = extract_tuple_profile(distance_matrix[i], m, all_minutiae ,k)
            tuples[str(m)] = ratios_angles

    return tuples



def match_two_point(ratios_base, angles_base, ratios_test, angles_test, th_range, th_angle):
    count = 0
    list_done = []
    for i in range(len(ratios_base)):
        check = True
        for j in range(len(ratios_base)):
            if j not in list_done:
                if ((ratios_test[i] >= ratios_base[j] - th_range)  * (ratios_test[i] <= ratios_base[j] + th_range)) == True and  ((angles_test[i] >= angles_base[j] - th_angle)  * (angles_test[i] <= angles_base[j] + th_angle)) == True:
                    count +=1
                    list_done.append(j)
                    check =  False
                    break
            if check == False:
                break
    return count
    
def match_tuples(tuple_base: dict, tuple_test: dict, th_range: float = .01, th_angle: float = 1.5):
  
    ratios_test = np.array([ratios for c, [ratios, _] in tuple_test.items()])
    angles_test = np.array([angles for c, [_, angles] in tuple_test.items()])
    point_test = np.array([c for c, [_, angles] in tuple_test.items()])
    num_point_test = len(point_test)
    
    ratios_base = np.array([ratios for c, [ratios, _] in tuple_base.items()])
    angles_base = np.array([angles for c, [_, angles] in tuple_base.items()])
    point_base = np.array([c for c, [_, angles] in tuple_base.items()])
    num_point_base = len(point_base)

    
    common_points_base = []
    common_points_test = []

    matrix_score_all_point= []
    list_score_all_point= []
    for i in range(num_point_test):
        list_score = []
        for j in range(num_point_base):
            # list_score_all_point.append(match_two_point(ratios_base[j],angles_base[j],ratios_test[i],angles_test[i],th_range, th_angle ))
            list_score.append(match_two_point(ratios_base[j],angles_base[j],ratios_test[i],angles_test[i],th_range, th_angle ))
        matrix_score_all_point.append(list_score)
    index = min(num_point_base,num_point_test)
    list_score_all_point =  np.array(matrix_score_all_point).reshape(-1)
    list_sorted = sorted(list_score_all_point, reverse= True)
    
    list_point_done_row = []
    list_point_done_column = []
    
    T = len(ratios_test[0])

    for k in range(index):
        for i in range(num_point_test):
            check1= True
            if i not in list_point_done_row:
                for j in range(num_point_base):
                    check2 = True
                    if j not in list_point_done_column and i not in list_point_done_row:
                        if matrix_score_all_point[i][j] == list_sorted[0]:
                           

                            num_column = num_point_base
                            num_row = num_point_test

                            for x in range(num_column):
                                if x not in list_point_done_column:
                                    list_sorted.remove(matrix_score_all_point[i][x])
                            for y in range(num_row):
                                if y == i:
                                    pass
                                else:
                                    if y not in list_point_done_row:
                                        list_sorted.remove(matrix_score_all_point[y][j])
                            list_point_done_row.append(i)
                            list_point_done_column.append(j)
                            if matrix_score_all_point[i][j] >= (T//2):
                                common_points_base.append(point_base[j])
                            common_points_test.append(point_test[i])
                            check1 =False
                            check2 = False
                    if check2 == False:
                        break
            if check1 == False:
                break
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
   

                        

                            



                    

