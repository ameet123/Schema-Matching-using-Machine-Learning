import pickle

import numpy as np


def Normalise(features):
    f_col = []
    for i in range(0, len(features[0])):
        column = features[:, i]
        maximum = max(column)
        # print maximum
        col = []
        for j in range(0, len(column)):
            if maximum == 0:
                col.append(column[j])
            else:
                col.append(round(float(column[j]) / maximum, 4))
        # print col
        f_col.append(col)
    return f_col


def features_to_file(run_type):
    if run_type == "test":
        FILE_TYPE = "Match"  # Train or Match
    elif run_type == "train":
        FILE_TYPE = "Train"
    dict = pickle.load(open("../Feature_Vectors/DataFeatures_" + FILE_TYPE + ".pickle", "rb"))
    f = []
    keys = []
    for key in dict.keys():
        keys.append(key)
        f.append(dict[key])
    features = np.array(f)
    print "size of original features: ", len(features), len(features[0])
    c_features = Normalise(features)
    print "size of normalise-transpose features: ", len(c_features), len(c_features[0])
    final_features = []
    for i in range(0, len(c_features[0])):
        # column = c_features[:][i]
        column = [row[i] for row in c_features]
        final_features.append(column)
    print "size of final features: ", len(final_features), len(final_features[0])
    norm_dict = {}
    for i in range(0, len(keys)):
        norm_dict[keys[i]] = final_features[i]
    # print norm_dict
    pickle.dump(norm_dict, open("../Feature_Vectors/normalised_features_" + FILE_TYPE.lower() + ".pickle", 'wb'))
    print "done"


features_to_file("test")
