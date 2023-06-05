import cv2
import fingerprint_enhancer
import fingerprint_feature_extractor
import numpy as np

from matching1 import extract_angle, extract_tuple_profile, generate_tuple_profile, match_tuples, match
import json
def predict(image_path):
    with open('data.json','r') as f:
        data = json.load(f)

    img_test = cv2.imread(image_path,0)
    try:
        out =  fingerprint_enhancer.enhance_Fingerprint(img_test)
        FeaturesTerm, FeaturesBif = fingerprint_feature_extractor.extract_minutiae_features(out, showResult= False)

        minutiae =  FeaturesTerm + FeaturesBif
        location_minutiae = []
        for j in range(len(minutiae)):
            location_minutiae.append((minutiae[j].locX, minutiae[j].locY))


        location_minutiae_bifurcation = []
        location_minutiae_termination = []

        for j in range(len(FeaturesTerm)):
            location_minutiae_termination.append((FeaturesTerm[j].locX, FeaturesTerm[j].locY))

        for k in range(len(FeaturesBif)):
            location_minutiae_bifurcation.append((FeaturesBif[k].locX, FeaturesBif[k].locY))

        feature_termination = generate_tuple_profile(location_minutiae,location_minutiae_termination,3)
        feature_bifurcation = generate_tuple_profile(location_minutiae,location_minutiae_bifurcation,3)
        feature = dict()
        feature['Termination']  = feature_termination
        feature['Bifurcation']  = feature_bifurcation
        list_db = list(data.values())
        list_key = list(data.keys())
        list_score =[]
        list_common_points = []
        for i in range(len(list_db)):
            common_points_base, common_points_test = match(feature, list_db[i], th_range = 0.1,th_angle=2)
            number_common_points = len(common_points_base)
            list_common_points.append(number_common_points)
            # list_score.append(common_points)
            a =len(list(feature.values())[1]) + len(list(feature.values())[0])
            b  = len(list(list_db[i].values())[1]) + len(list(list_db[i].values())[0])
            list_score.append(number_common_points/((a+b)/2))
        file_result = None
        score = None
        if max(list_score)> 0:
            file_result = list_key[list_score.index(max(list_score))]
            score =  max(list_score)

        return file_result, score
    except:
        return None, None
