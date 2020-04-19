# -*- encoding: utf-8 -*-

'''
    The classifier module.
'''

# General imports
import numpy

import sklearn.tree
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import export_text
import pickle

# Custom imports
import sample.config as config

class Classifier:

    def train(self, *args):
        raise NotImplementedError("Method must be implemented.")  

    def predict(self, *args):
        raise NotImplementedError("Method must be implemented.")


class DecisionTree(Classifier):

    def __init__(self):
        try:
            self.dtc = pickle.load(open(config.CLASSIFIER_MODEL_FILENAME, 'rb'))
        except: 
            self.dtc = sklearn.tree.DecisionTreeClassifier()
            self.samples = self.__get_samples()
            self.__train()       

    def __train(self, k=None):

        if k is None:
            k = 5


        training_data, training_target, test_samples = self.__prepare_samples()
        scores = cross_val_score(self.dtc, training_data, training_target, cv=k)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

        #X, Y = sklearn.model_selection.train_test_split(self.samples)

        target_list = []
        data_list = []       
        for sample in self.samples:
            data = [sample[0], sample[1], sample[2], sample[3]]
            data_list.append(data)
            target = sample[4]           
            target_list.append(target)


        self.dtc = self.dtc.fit(data_list, target_list)
        pickle.dump(self.dtc, open(config.CLASSIFIER_MODEL_FILENAME, 'wb'))

        '''
        cv = KFold(n_splits=5)
        tree_model = tree.DecisionTreeClassifier(max_depth=3)
        print(titanic_train.describe())
        fold_accuracy = []
        for train_index, valid_index in cv.split(X_train):
            train_x,test_x = X_train.iloc[train_index],X_train.iloc[valid_index]
            train_y,test_y= y_train.iloc[train_index], y_train.iloc[valid_index]

            model = tree_model.fit(train_x,train_y)
            valid_acc = model.score(test_x,test_y)
            fold_accuracy.append(valid_acc)
            print(confusion_matrix(y_test,model.predict(X_test)))

        print("Accuracy per fold: ", fold_accuracy, "\n")
        print("Average accuracy: ", sum(fold_accuracy)/len(fold_accuracy))
        dot_data = StringIO()

        #joblib.dump(self.dtc, config.CLASSIFIER_MODEL_FILENAME) 
        '''

    def predict(self, sample):
        return self.dtc.predict(sample)

    def plot(self):
        tree.plot_tree(self.dtc) 


    def __prepare_samples(self):

        training_samples, test_samples = sklearn.model_selection.train_test_split(self.samples)

        target_list = []
        data_list = []       
        for sample in training_samples:
            data = [sample[0], sample[1], sample[2], sample[3]]
            data_list.append(data)
            target = sample[4]           
            target_list.append(target) 

        return data_list, target_list, test_samples


    def __get_samples(self):

        return ([
        [0.25664605873261204, 0.698771336297241, 0.1292099582321753, 4, 1], 
        [0.24522130968820408, 0.6983437358345829, 0.1301658689474827, 0, 1], 
        [0.2047752061718542, 0.7190417056722007, 0.13955235016980783, 4, 1], 
        [0.21452859350850076, 0.7049612928744985, 0.13787840204952506, -2, 1], 
        [0.251437386060861, 0.67860415778135, 0.1223018094461464, 4, 1], 
        [0.28193479422768575, 0.5372140135675123, 0.10576997453242554, -3, 1], 
        [0.23944642028761404, 0.6707718411872335, 0.1190646757839051, 2, 1], 
        [0.1919047619047619, 0.7226084478456395, 0.1461184591691715, 0, 1], 
        [0.2704095470572281, 0.5723720180148288, 0.13154748888402945, -1, 1], 
        [0.20214117220105243, 0.6987573485408527, 0.14415176122757492, 0, 1], 
        [0.24694143167028199, 0.6654596061896297, 0.12969868671054086, 4, 1],
        [0.36510590858416947, 0.7639455171381531, 0.22466904233159463, -1, 1], 
        [0.27435940660822655, 0.6878467516038673, 0.1219316766083829, 1, 1], 
        [0.26360564036825546, 0.7102061337355455, 0.1309303718322271, 2, 1], 
        [0.42586436170212766, 0.6510803957284188, 0.17426721315818358, 1, 1], 
        [0.39288354898336414, 0.6928731878542995, 0.17296571239243147, 3, 1], 
        [0.37767069733612146, 0.7064714378770286, 0.1833506638594079, 2, 1], 
        [0.28844926611359284, 0.6947442497156188, 0.14451380950985276, 4, 1], 
        [0.29253321779318314, 0.6968136649871007, 0.14226123643292166, -2, 1], 
        [0.27529761904761907, 0.6454981452040275, 0.11008978540081331, -1, 1], 
        [0.23844731977818853, 0.6351755585955311, 0.11703217209213782, 0, 1], 
        [0.2730499681441704, 0.8055228758169934, 0.26143316222194396, 2, 1], 
        [0.3675342008675342, 0.7886298837888915, 0.22135122227911658, 2, 1], 
        [0.3298265042451089, 0.7986218550094912, 0.23775765332296508, 4, 1], 
        [0.37069803616566205, 0.8316234965006197, 0.2477924894660475, -1, 1], 
        [0.29687246799546263, 0.566037331963353, 0.22578076632819527, -2, -1],
        [0.20287126382678278, 0.42589964059869884, 0.13480088226610396, 4, -1], 
        [0.24073769142104395, 0.5279338000590112, 0.1498819957390894, 14, -1],
        [0.17805755395683454, 0.20178670085790826, 0.13535847599433648, 24, -1],
        [0.21816630321418412, 0.47224480404939023, 0.13232226676748798, 13, -1],
        [0.2608538611572636, 0.5553922926135284, 0.1475356053289181, 2, -1],
        [0.15692410119840214, 0.5640170705532956, 0.2705055488198596, 20, -1], 
        [0.2606350184956843, 0.5974953908233903, 0.1716538522851292, 10, -1], 
        [0.2093900481540931, 0.4285256916104886, 0.22048761845617346, 10, -1], 
        [0.35266359060402686, 0.5324074559945894, 0.23512386325014376, -1, -1],
        [0.27204100006925686, 0.7170680084661156, 0.2682858853749853, 14, -1], 
        [0.2623951182303585, 0.7106848236123201, 0.2670994880983323, 16, -1], 
        [0.29614676299759174, 0.699478030867932, 0.2693178791089748, 17, -1], 
        [0.2853456092627467, 0.619168811499178, 0.27120444898630935, 26, -1], 
        [0.29422757475083056, 0.7205243518249455, 0.2712562518387761, 17, -1], 
        [0.24591423740970336, 0.6588382352941178, 0.28466447928447824, 36, -1], 
        [0.04241306638566913, 0.7254560954816709, 0.4681092860803194, 78, -1], 
        [0.4467269729512945, 0.8385452056134176, 0.3847698099858501, 5, 1], 
        [0.03248752848432592, 0.6928352383607472, 0.46459785480123494, 62, -1], 
        [0.036456619912073454, 0.7222635075359102, 0.4847284248605396, 68, -1], 
        [0.0909699385967465, 0.8382823378871702, 0.4653907790346667, 44, -1], 
        [0.3035006605019815, 0.6245300731827008, 0.25391180654338547, 14, -1], 
        [0.3277804410354746, 0.5796924400473169, 0.24608629688281092, 4, -1], 
        [0.09409140568099053, 0.5844977565288332, 0.2775527094411454, 63, -1], 
        [0.20893719806763286, 0.7239404188812733, 0.29536895674300256, 25, -1], 
        [0.3052791364479676, 0.6110453905319033, 0.2645673564400268, 14, -1], 
        [0.24175182481751825, 0.7087651163524991, 0.27611648432958086, 11, -1], 
        [0.2655172413793103, 0.6669093305771506, 0.2715596926425914, 13, -1], 
        [0.1383147853736089, 0.6238914698248598, 0.3013982929203106, 46, -1], 
        [0.06315653521611848, 0.488840771482417, 0.2679894144138056, 58, -1], 
        [0.2708140610545791, 0.7335778034527218, 0.27325277928065195, 10, -1], 
        [0.05364062818682439, 0.42884365913665845, 0.2856382691007437, 87, -1], 
        [0.3001694132142307, 0.7296813851245988, 0.2780801228942281, 18, -1], 
        [0.3567516933275688, 0.6382026209797189, 0.2880532071683832, 18, -1], 
        [0.34148066645708897, 0.7494284618335253, 0.27295128577746886, 8, -1]
        ])
         

