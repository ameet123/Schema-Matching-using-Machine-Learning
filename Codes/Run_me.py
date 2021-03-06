'''

This run me file integrates one to one and many to one mappings.

'''

import csv
import pickle
from collections import defaultdict

import editdistance
import numpy as np
from scipy.spatial import distance
from sklearn.metrics.pairwise import cosine_similarity

from minisom import MiniSom
from normalise import Normalise

# Training Data
dataFeaturePath = '../Feature_Vectors/DataFeatures_Train.pickle'
DataFeatures = pickle.load(open(dataFeaturePath, 'rb'))

# Test Data
testFeaturesPath = '../Feature_Vectors/DataFeatures_Match.pickle'
TestFeatures = pickle.load(open(testFeaturesPath, 'rb'))

Train_set = [k for k in DataFeatures.keys()]
Test_set = [k for k in TestFeatures.keys()]

global edit_distance
global cosine_distance
global euc_distance

edit_distance = {}
euc_distance = {}
cosine_distance = {}
missing_attributes = []


def calculate_edit_distance(test_names_features, train_names_features):
    # Calculating edit distance of a test attribute from all train attributes.
    for test_name in test_names_features.keys():
        edit_distance[test_name] = {}

        if train_names_features == {}:
            edit_distance[test_name]['None'] = 1
            missing_attributes.append(test_name)

        else:
            for name in train_names_features.keys():
                edit_distance[test_name][name] = editdistance.eval(test_name, name)

    return edit_distance


def cosine_euc_distance(test_names_features, train_names_features):
    # Calculating cosine and euclidean distance of a test attribute from all train attributes.

    for test_name in test_names_features.keys():
        cosine_distance[test_name] = {}
        euc_distance[test_name] = {}

        if train_names_features == {}:
            cosine_distance[test_name]['None'] = 1
            euc_distance[test_name]['None'] = 1
            missing_attributes.append(test_name)
        else:
            for name in train_names_features.keys():

                test_nd = np.asarray(test_names_features[test_name]).reshape(1,-1)
                train_nd = np.asarray(train_names_features[name]).reshape(1,-1)
                # print "Cosing=> test shape:%s train type:%s" % (test_nd.shape,train_nd.shape)
                cosine_distance[test_name][name] = \
                        cosine_similarity(test_nd, train_nd)[0][0]
                # cosine_distance[test_name][name] = \
                #     cosine_similarity(test_names_features[test_name], train_names_features[name])[0][0]
                euc_distance[test_name][name] = distance.euclidean(test_names_features[test_name],
                                                                   train_names_features[name])

    return cosine_distance, euc_distance


def cal_probability(distance_dic, name):
    file_path = open('../Results/Distances/All_distances_combined/' + name + '.csv', 'w')
    Out = csv.writer(file_path, delimiter=',')

    new_row = ['test_attribute', 'train_attribute', 'distance', 'probability']
    Out.writerow(new_row)
    for test_attribute in distance_dic.keys():
        # print test_attribute
        # print distance_dic[test_attribute].values()
        total = sum(distance_dic[test_attribute].values())
        # print total
        for train_attribute in distance_dic[test_attribute].keys():
            if total == 0:
                prob = 1
            else:
                prob = 1 - (distance_dic[test_attribute][train_attribute] / float(total))
            new_row = [test_attribute, train_attribute, distance_dic[test_attribute][train_attribute], prob]
            Out.writerow(new_row)
    file_path.close()


# Global Dictionary mapping an attribute to possible smaller features (one --> many attributes)
Global_Dictionary = {}
Global_Dictionary[('Name', 'PatientName')] = ['First Name', 'First_Name', 'FName', 'F_Name', 'Last_Name', 'Last Name',
                                              'LName', 'L_Name']
Global_Dictionary[('Address', 'Location', 'Addr', 'Residence', 'Loc')] = ['Street Name', 'S_Name', 'St_Name',
                                                                          'Str_Name', 'Stree_Name', 'StName', 'St_No',
                                                                          'ST_Number', 'Street_No', 'S_No', 'S_Number',
                                                                          'Street Number', 'StNumber', 'StNo',
                                                                          'Apt_Num', 'Apartment_Number',
                                                                          'Apartment Number', 'Apartment No',
                                                                          'Apt_Number', 'Apt_No']

OnetoMany = {}
flag = 0
for keys, values in Global_Dictionary.items():
    for k in keys:
        for attributes in Train_set:
            parent = 'tr_' + k
            if (attributes.lower() == parent.lower()):
                flag = 1
                OnetoMany[parent] = []
                print attributes
                print "has a possibility of adding to"
                for test_attributes in Test_set:
                    for val in values:
                        child = 'ts_' + val
                        if (test_attributes.lower() == child.lower()):
                            print test_attributes
                            OnetoMany[parent].append(child)

if flag == 0: print "no one to many mappings possible"

ManytoOne = {}
flag = 0
for keys, values in Global_Dictionary.items():
    for k in keys:
        for attributes in Test_set:
            parent = 'tr_' + k
            if (attributes.lower() == parent.lower()):
                flag = 1
                ManytoOne[parent] = []
                print attributes
                print "has a possibility of adding to"
                for test_attributes in Train_set:
                    for val in values:
                        child = 'ts_' + val
                        if (test_attributes.lower() == child.lower()):
                            print test_attributes
                            ManytoOne[attributes].append(test_attributes)

if flag == 0: print "no many to one mappings possible"

print 'One to Many Mappings:', OnetoMany
print 'Many to One Mappings:', ManytoOne

# Merge the many items keys and check against them
the_manies = OnetoMany.keys() + ManytoOne.keys()
Remaining_Features = []
for key in Train_set:
    # print key
    if key not in the_manies:
        Remaining_Features.append(key.lower())
    # for k in OnetoMany.keys() or ManytoOne.values():
    #     print "Many-x key:%s" % k
    #     if key != k:
    #         Remaining_Features.append(key.lower())
for key in Test_set:
    if key not in ManytoOne.keys() or key not in OnetoMany.values():
        Remaining_Features.append(key.lower())

print "====Remaining Features=========: %d" % len(Remaining_Features)
print Remaining_Features
# List of all features in training and testing data
InitFeatures = []
all_attributes = []
for key, val in DataFeatures.items():
    attr = key.lower()
    print "Working on attri:%s" % attr
    if attr in Remaining_Features:
        print '---------', attr
        InitFeatures.append(val)
        all_attributes.append(key)

for key, val in TestFeatures.items():
    attr = key.lower()
    if attr in Remaining_Features:
        print '---------', attr
        InitFeatures.append(val)
        all_attributes.append(key)

print "---All attrib: %d:" % len(all_attributes)
print all_attributes
print "------------------------------------------"

print "--- Init Features ---- : %d" % len(InitFeatures)
print InitFeatures
# Normalise all features after appending them together
c_features = Normalise(np.array(InitFeatures))

Features = []
for i in range(0, len(c_features[0])):
    # column = c_features[:][i]
    column = [row[i] for row in c_features]
    Features.append(column)

print "=== Size of Features used in SOM: %d" % len(Features)
# Self Organising Map
# x = input('enter x value for grid: ')
# y = input('enter y value for grid: ')
# iteration = input("Input number of iterations: ")
x = 6
y = 6
iteration = 100
# Create a SOM
som = MiniSom(x, y, 20, sigma=0.3, learning_rate=0.5)
print "Training..."
som.train_random(Features, iteration)  # trains the SOM with 100 iterations
print "...ready!"

# Map the output neuron position to a unique cluster id. (0,0) --> 0, (0,1) --> 1 and so on.
feature_map = {}
k = 0

for i in range(x):
    for j in range(y):
        feature_map[(i, j)] = k
        k += 1

# print feature_map, '\n'


# Write the attribute name and its corresponding id. DataFeatures is the dictionary (attribute, feature). attribute_cluster is the dictionary (attribute, cluster_id). If the feature being mapped is same as the feature in the dictionary, save its winner ID in the dictionary.

# attribute_clusters = defaultdict(lambda: defaultdict())
attribute_clusters = defaultdict(dict)
for i in range(0, len(all_attributes)):
    # print feature_map[som.winner(Features[i])]
    attribute_clusters[feature_map[som.winner(Features[i])]][all_attributes[i]] = Features[i]

# print attribute_cluster[]

print "Type of attr cluster:%s Size:%d attrib_values:%d" % (
type(attribute_clusters), len(attribute_clusters), len(attribute_clusters.values()))
print attribute_clusters
print "attrib values===="
print attribute_clusters.values()
pickle.dump(attribute_clusters, open('../Results/17_FinalSOM_with_normal_' + str(int(x * y)) + '.pickle', 'w'))
# output_file = open('FinalSOM_with_normal_' + int(x*y) + '.txt', 'w')


for cluster_id in attribute_clusters.values():

    test_names_features = {}
    train_names_features = {}

    for attribute in cluster_id.keys():
        if attribute in Test_set:
            test_names_features[attribute] = cluster_id[attribute]
        else:
            train_names_features[attribute] = cluster_id[attribute]

    edit_distance = calculate_edit_distance(test_names_features, train_names_features)
    cosine_distance, euc_distance = cosine_euc_distance(test_names_features, train_names_features)

print euc_distance['ts_s_fuh_measure_end_date']

cal_probability(edit_distance, 'FinalSOM_edit_' + str(x * y))
cal_probability(cosine_distance, 'FinalSOM_cosine_' + str(x * y))
cal_probability(euc_distance, 'FinalSOM_euc_' + str(x * y))
# print 'All one to one mappings saved in the file: ', OneToOne + '.csv'


'''
output_file.write('One to Many Mappings: \nTrain Data		Test Data\n')
for key,val in OneToMany.items():
    output_file.write(str(key) + '		')
    for v in val:
        output_file.write(str(v) + ',')
    output_file.write('\n')

output_file.write('Many to One Mappings: \nTrain Data		Test Data\n')
for key,val in ManyToOne.items():
    for v in key:
        output_file.write(str(v) + ',')
    output_file.write('		' + str(val)) 
    output_file.write('\n')

'''
