# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 13:11:53 2020

@author: AhrensL
"""

import DataReader as reader
import numpy as np

import matplotlib.pyplot as plt8

from sklearn.model_selection import train_test_split
import Util as u
from sklearn.neural_network import MLPRegressor

def prepare_data(covid_data):
    
    covid_data = covid_data.groupby(['Kalenderwoche', 'Bundesland']).sum()
    kalenderwoche = np.array(covid_data.index.get_level_values(0))
    bundesland = np.array(covid_data.index.get_level_values(1))
    covid_data.loc[:,('KW')] = kalenderwoche
    covid_data.loc[:,('Bundesland')] = bundesland
    
    
    
    
    
    
    
    #ab kalenderwoche 12 werden Maßnahmen getroffen
    #r-0-Faktor?
    r_null_faktor = []
    massnahmen = []
    maskenpflicht = []
    kontaktbeschraenkung = []
    kalenderwochen_nr = []
    for indexes, row in covid_data.iterrows():
        kalenderwoche = row['KW']
        anzahlFall = row ['AnzahlFall']
        anzahlGenesen = row['AnzahlGenesen']
        bundesland_to_filter = row['Bundesland']
        if anzahlGenesen != 0:
            r_null = anzahlFall / anzahlGenesen
            r_null_faktor.append(r_null)
        else:
            r_null_faktor.append(anzahlFall)
        kalenderwoche_nr = int(kalenderwoche)
        kalenderwochen_nr.append(kalenderwoche_nr)
        if kalenderwoche_nr >= 12:
            massnahmen.append(1)
        else:
            massnahmen.append(0)
        if kalenderwoche_nr >= 18:
            maskenpflicht.append(1)
        else:
            maskenpflicht.append(0)
        if kalenderwoche_nr >= 17 and kalenderwoche_nr < 26:
            kontaktbeschraenkung.append(1)
        else:
            kontaktbeschraenkung.append(0)
       
        
    
        
    covid_data.loc[:,('Großveranstaltung')] = massnahmen
    covid_data.loc[:,('MaskenpflichtJN')] = maskenpflicht
    covid_data.loc[:,('KontaktbeschraenkungJN')] = kontaktbeschraenkung #Treffen von bis zu 10 Personen gilt hier als keine Kontaktbeschränkung
    covid_data.loc[:,('Kalenderwoche')] = kalenderwochen_nr
    covid_data.loc[:,('Kalenderwoche_for_filter')] = kalenderwochen_nr
    covid_data.loc[:,('R_Null_Faktor')] = r_null_faktor
    covid_data = covid_data.loc[covid_data['Kalenderwoche'] >= 10  ] 
    covid_data = covid_data.loc[covid_data['Kalenderwoche'] <22  ] 
    return covid_data

def print_prediction(column_to_predict, kalenderwoche, labels_pred):
    str_to_predict = column_to_predict +' in Kalenderwoche '+str(kalenderwoche)
    print(
    str_to_predict + ' in Baden-Wüttemberg: '       + str(labels_pred[0][0])+'\n' +
    str_to_predict + ' in Bayern: '                 + str(labels_pred[0][1])+'\n' +
    str_to_predict + ' in Berlin: '                 + str(labels_pred[0][2])+'\n' +
    str_to_predict + ' in Brandenburg: '            + str(labels_pred[0][3])+'\n' +
    str_to_predict + ' in Bremen: '                 + str(labels_pred[0][4])+'\n' +
    str_to_predict + ' in Hamburg: '                + str(labels_pred[0][5])+'\n' +
    str_to_predict + ' in Hessen: '                 + str(labels_pred[0][6])+'\n' +
    str_to_predict + ' in Mecklenburg-Vorpommern: ' + str(labels_pred[0][7])+'\n' +
    str_to_predict + ' in Niedersachsen: '          + str(labels_pred[0][8])+'\n' +
    str_to_predict + ' in Nordrhein-Westfahlen: '   + str(labels_pred[0][9])+'\n' +
    str_to_predict + ' in Rheinland-Pfalz: '        + str(labels_pred[0][10])+'\n' +
    str_to_predict + ' in Saarland: '               + str(labels_pred[0][11])+'\n' +
    str_to_predict + ' in Sachsen: '                + str(labels_pred[0][12])+'\n' +
    str_to_predict + ' in Sachsen-Anhalt: '         + str(labels_pred[0][13])+'\n' +
    str_to_predict + ' in Schleswig-Holstein: '     + str(labels_pred[0][14])+'\n' +
    str_to_predict + ' in Thüringen: '              + str(labels_pred[0][15]))
    
   
    #zum Plotten der Loss-Kurve:
    #pd.DataFrame(mlp_regr.loss_curve_).plot()
def predict_data(covid_data, column_to_predict, kalenderwoche, grossveranstaltung,maskenpflicht,kontaktbeschraenkung):
    #features sind für jedes Bundesland gleich, dürfen aber nur die Größe der Label haben
    features_dataframe = covid_data.loc[covid_data['Bundesland'] == 'Bayern']
    features_dataframe = features_dataframe.filter(items = ['Kalenderwoche', 'Großveranstaltung', 'MaskenpflichtJN', 'KontaktbeschraenkungJN'])

    
    labels_dataframe = covid_data.filter(items = [column_to_predict])
    labels_array1 = np.array(labels_dataframe)
    
    features = np.array(features_dataframe)
    labels = np.reshape(labels_array1, (-1,16))
    features_train, features_test, labels_train, labels_test = train_test_split(features, labels, test_size=0.2)
       
    my_hiddenlayer_size = (80,10)
    mlp_regr = MLPRegressor(hidden_layer_sizes= my_hiddenlayer_size, activation='relu',random_state=1, max_iter=500, solver ='lbfgs', learning_rate='constant').fit(features_train, labels_train)
    
    #mlp_labels_predict = mlp_regr.predict(X = feature_to_predict)
    test_prediction = mlp_regr.predict(X= features)
    feature_to_predict = np.array([[kalenderwoche,grossveranstaltung,maskenpflicht,kontaktbeschraenkung]])
    labels_pred = mlp_regr.predict(X= feature_to_predict)
    print_prediction(column_to_predict, kalenderwoche, labels_pred)
    
    print('Metrik neuronales Netz: ')
    print('    Score: '+ str(mlp_regr.score(features_test, labels_test)))
    print('    Loss: '+str(mlp_regr.loss_))
    kalenderwoche_to_plot = features[:,0]
    
    plt8.scatter(kalenderwoche_to_plot, labels[:,8], color= 'blue')
    
    plt8.scatter(kalenderwoche_to_plot, test_prediction[:,8], color = 'red')
    
    
    plt8.ylabel('Anzahl der Fälle')
    plt8.xlabel('Kalenderwoche')
    plt8.title('Tatsächliche und vorausgesagte '+column_to_predict+' neuronales Netz Niedersachsen (Blau: Tatsächlich, Rot: Vorausgesagt)')
    plt8.show()
    
    
    u.save_model(mlp_regr, 'predict_data_multi_label_hiddenlayersize_'+str(my_hiddenlayer_size))
    plt8.savefig("Result\\" + 'predict_data_multi_label_neuronales_netz_niedersachsen_' + ".png")
    
def predict_multi_label(kalenderwoche, column_to_predict,covid_data, grossveranstaltung,maskenpflicht,kontaktbeschraenkung):
    print("Anhand eines Features wird ein Label mit den Fällen für jedes Bundesland vorausgesagt...")
    dataframe = prepare_data(covid_data)
    predict_data(dataframe, column_to_predict, kalenderwoche,grossveranstaltung,maskenpflicht,kontaktbeschraenkung)


   
 
