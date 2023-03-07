import pandas as pd
from datetime import datetime, date
from datetime import timedelta
import matplotlib.pyplot as plt
from scipy.stats import linregress
import pymongo
from pymongo import MongoClient
import certifi
import configparser
import json
import numpy as np
import streamlit as st
from PIL import Image

CONN_ID='dev_postgres'

def main():
    def get_data():
        upload_file = st.sidebar.file_uploader('Upload your file.xlsx')
        if upload_file is None:
            st.header(":red[CEC : Capacité d'Echange Cathionique]")
        return (upload_file)
    file = get_data()
    if file is None:
        st.header("Dosage des Bases Echangeables par ICP extraites par Acétate d'Ammonium ")
    else:
        irda = pd.read_excel(file)
        def DataFrame():
            CA = pd.DataFrame(columns=['Date','Echantillon', 'Lecture ICP mg/l', 'Lect. ICP-BL mg/l', 'Poids g'])
            for i in range(len(irda)):
                CA['Date'] = irda['Date']
                CA['Echantillon'] = irda['Echantillon']
                CA['Lecture ICP mg/l'] = None
                CA['Lect. ICP-BL mg/l'] = None
                CA['Poids g'] = irda['Poids']

            return CA

        dataFrame=DataFrame()

        def get_data_Ca():

           #Calculer Lect. ICP-BL mg/l
            JDD_CA = dataFrame.copy(deep=True)
            JDD_CA['Lecture ICP mg/l'] = irda['Ca (mg/l)']
            JDD_CA["Split Echantillon"] = JDD_CA["Echantillon"].str.split("-", n=1, expand=False)
            CA_List = JDD_CA.values.tolist()
            data_LB = []
            Echantillon = []
            for i in (CA_List):
                Echantillon.append(i[1])
            for k in Echantillon:
                if k[0:2] == 'BL':
                    data_LB.append(k)
            data_BLanc = []
            for i in range(len(data_LB)):
                for k in range(len(CA_List)):
                    if CA_List[k][1] == data_LB[i]:
                        data_BLanc.append(data_LB[i])
                        for l in [2]:
                            data_BLanc.append(CA_List[k][l])
            step, size = 2, 2
            JDD_LB = []
            for i in range(0, len(data_BLanc), step):
                JDD_LB.append(data_BLanc[i: i + size])

            Blanc = pd.DataFrame(JDD_LB, columns=['Echantillon', 'Lecture ICP mg/l'])
            Blanc["Split"] = Blanc["Echantillon"].str.split("-", n=1, expand=False)

            for i in range(len(JDD_CA)):
                for j in range(len(Blanc)):
                    if JDD_CA["Split Echantillon"][i][1] == Blanc["Split"][j][1]:
                        JDD_CA["Lect. ICP-BL mg/l"][i] = JDD_CA["Lecture ICP mg/l"][i] - Blanc["Lecture ICP mg/l"][j]

            JDD_CA['Ca (cmol+/Kg)'] = JDD_CA['Lect. ICP-BL mg/l'] * (0.25 / JDD_CA['Poids g']) * (1 / 20.04) * (1 / 10) * (
                    1000 / 1)
            JDD_CA = JDD_CA.drop(['Split Echantillon'], axis=1)
            return (JDD_CA)

        def get_data_Mg():
            JDD_Mg = dataFrame.copy(deep=True)
            JDD_Mg['Lecture ICP mg/l'] = irda['Mg (mg/l)']
            JDD_Mg["Split Echantillon"] = JDD_Mg["Echantillon"].str.split("-", n=1, expand=False)
            CA_List_Mg = JDD_Mg.values.tolist()
            data_LB = []
            Echantillon = []
            for i in (CA_List_Mg):
                Echantillon.append(i[1])
            for k in Echantillon:
                if k[0:2] == 'BL':
                    data_LB.append(k)
            data_BL = []
            for i in range(len(data_LB)):
                for k in range(len(CA_List_Mg)):
                    if CA_List_Mg[k][1] == data_LB[i]:
                        data_BL.append(data_LB[i])
                        for l in [2]:
                            data_BL.append(CA_List_Mg[k][l])
            step, size = 2, 2
            JDD_LB = []
            for i in range(0, len(data_BL), step):
                # slicing list
                JDD_LB.append(data_BL[i: i + size])

            Blanc = pd.DataFrame(JDD_LB, columns=['Echantillon', 'Lecture ICP mg/l'])
            Blanc["Split"] = Blanc["Echantillon"].str.split("-", n=1, expand=False)
            for i in range(len(JDD_Mg)):
                for j in range(len(Blanc)):
                    if JDD_Mg["Split Echantillon"][i][1] == Blanc["Split"][j][1]:
                        JDD_Mg["Lect. ICP-BL mg/l"][i] = JDD_Mg["Lecture ICP mg/l"][i] - Blanc["Lecture ICP mg/l"][j]
            JDD_Mg['Mg (cmol+/Kg)'] = JDD_Mg['Lect. ICP-BL mg/l'] * (0.25 / JDD_Mg['Poids g']) * (1 / 20.04) * (
                        1 / 10) * (1000 / 1)
            JDD_Mg = JDD_Mg.drop(['Split Echantillon'], axis=1)

            return JDD_Mg

        def get_data_K():
            JDD_K = dataFrame.copy(deep=True)
            JDD_K['Lecture ICP mg/l'] = irda['K (mg/l)']
            JDD_K["Split Echantillon"] = JDD_K["Echantillon"].str.split("-", n=1, expand=False)
            K_List = JDD_K.values.tolist()
            data_LB = []
            Echantillon = []
            for i in (K_List):
                Echantillon.append(i[1])
            for k in Echantillon:
                if k[0:2] == 'BL':
                    data_LB.append(k)
            data_BL = []
            for i in range(len(data_LB)):
                for k in range(len(K_List)):
                    if K_List[k][1] == data_LB[i]:
                        data_BL.append(data_LB[i])
                        for l in [2]:
                            data_BL.append(K_List[k][l])
            step, size = 2, 2
            JDD_LB = []
            for i in range(0, len(data_BL), step):
                # slicing list
                JDD_LB.append(data_BL[i: i + size])
            Blanc = pd.DataFrame(JDD_LB, columns=['Echantillon', 'Lecture ICP mg/l'])
            Blanc["Split"] = Blanc["Echantillon"].str.split("-", n=1, expand=False)
            for i in range(len(JDD_K)):
                for j in range(len(Blanc)):
                    if JDD_K["Split Echantillon"][i][1] == Blanc["Split"][j][1]:
                        JDD_K["Lect. ICP-BL mg/l"][i] = JDD_K["Lecture ICP mg/l"][i] - Blanc["Lecture ICP mg/l"][j]
            JDD_K['K (cmol+/Kg)'] = JDD_K['Lect. ICP-BL mg/l'] * (0.25 / JDD_K['Poids g']) * (1 / 20.04) * (1 / 10) * (
                        1000 / 1)
            JDD_K = JDD_K.drop(['Split Echantillon'], axis=1)
            return JDD_K

        def get_data_Na():

            JDD_Na = dataFrame.copy(deep=True)
            JDD_Na['Lecture ICP mg/l'] = irda['Na(mg/l)']
            JDD_Na["Split Echantillon"] = JDD_Na["Echantillon"].str.split("-", n=1, expand=False)
            Na_List = JDD_Na.values.tolist()
            data_LB = []
            Echantillon = []
            for i in (Na_List):
                Echantillon.append(i[1])
            for k in Echantillon:
                if k[0:2] == 'BL':
                    data_LB.append(k)
            data_BL = []
            for i in range(len(data_LB)):
                for k in range(len(Na_List)):
                    if Na_List[k][1] == data_LB[i]:
                        data_BL.append(data_LB[i])
                        for l in [2]:
                            data_BL.append(Na_List[k][l])
            step, size = 2, 2
            JDD_LB = []
            for i in range(0, len(data_BL), step):
                # slicing list
                JDD_LB.append(data_BL[i: i + size])
            Blanc = pd.DataFrame(JDD_LB, columns=['Echantillon', 'Lecture ICP mg/l'])
            Blanc["Split"] = Blanc["Echantillon"].str.split("-", n=1, expand=False)
            for i in range(len(JDD_Na)):
                for j in range(len(Blanc)):
                    if JDD_Na["Split Echantillon"][i][1] == Blanc["Split"][j][1]:
                        JDD_Na["Lect. ICP-BL mg/l"][i] = JDD_Na["Lecture ICP mg/l"][i] - Blanc["Lecture ICP mg/l"][j]
            JDD_Na['Na (cmol+/Kg)'] = JDD_Na['Lect. ICP-BL mg/l'] * (0.25 / JDD_Na['Poids g']) * (1 / 20.04) * (
                        1 / 10) * (1000 / 1)
            JDD_Na = JDD_Na.drop(['Split Echantillon'], axis=1)
            return JDD_Na

        def get_data_Al():
            JDD_Al = dataFrame.copy(deep=True)
            JDD_Al['Lecture ICP mg/l'] = irda['Al (mg/l)']
            JDD_Al["Split Echantillon"] = JDD_Al["Echantillon"].str.split("-", n=1, expand=False)
            Al_List = JDD_Al.values.tolist()
            data_LB = []
            Echantillon = []
            for i in (Al_List):
                Echantillon.append(i[1])
            for k in Echantillon:
                if k[0:2] == 'BL':
                    data_LB.append(k)
            data_BL = []
            for i in range(len(data_LB)):
                for k in range(len(Al_List)):
                    if Al_List[k][1] == data_LB[i]:
                        data_BL.append(data_LB[i])
                        for l in [2]:
                            data_BL.append(Al_List[k][l])
            step, size = 2, 2
            JDD_LB = []
            for i in range(0, len(data_BL), step):
                # slicing list
                JDD_LB.append(data_BL[i: i + size])

            Blanc = pd.DataFrame(JDD_LB, columns=['Echantillon', 'Lecture ICP mg/l'])
            Blanc["Split"] = Blanc["Echantillon"].str.split("-", n=1, expand=False)
            for i in range(len(JDD_Al)):
                for j in range(len(Blanc)):
                    if JDD_Al["Split Echantillon"][i][1] == Blanc["Split"][j][1]:
                        JDD_Al["Lect. ICP-BL mg/l"][i] = JDD_Al["Lecture ICP mg/l"][i] - Blanc["Lecture ICP mg/l"][j]
            JDD_Al['Al (cmol+/Kg)'] = JDD_Al['Lect. ICP-BL mg/l'] * (0.25 / JDD_Al['Poids g']) * (1 / 20.04) * (
                        1 / 10) * (1000 / 1)
            JDD_Al = JDD_Al.drop(['Split Echantillon'], axis=1)

            return JDD_Al

        ## Rassembler les différents minéraux calculés en "(cmol+/Kg)"

        JDD_K = get_data_K()
        JDD_CA = get_data_Ca()
        JDD_Mg = get_data_Mg()
        JDD_Na = get_data_Na()
        JDD_Al = get_data_Al()

        def dataset_mineraux():
            mineral = pd.DataFrame(columns=['Date','Echantillon', 'K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)','Na (cmol+/Kg)','Al (cmol+/Kg)'])
            mineral['Date']=dataFrame['Date']
            mineral['Echantillon']=dataFrame['Echantillon']
            mineral['K (cmol+/Kg)'] = JDD_K['K (cmol+/Kg)']
            mineral['Ca (cmol+/Kg)'] = JDD_CA['Ca (cmol+/Kg)']
            mineral['Mg (cmol+/Kg)'] = JDD_Mg['Mg (cmol+/Kg)']
            mineral['Na (cmol+/Kg)'] = JDD_Na['Na (cmol+/Kg)']
            mineral['Al (cmol+/Kg)'] = JDD_Al['Al (cmol+/Kg)']

            return mineral

        # Separation des référentiels

                ## Référentiel  46B

        JDD_Minéraux = dataset_mineraux()

        def ref_46B():
            JDD_Minéraux_List = JDD_Minéraux.values.tolist()
            data_46B = []
            Echantillon = []
            for i in (JDD_Minéraux_List):
                Echantillon.append(i[1])
            for k in Echantillon:
                if k[0:3] == '46B':
                    data_46B.append(k)
            data_46B1 = []
            for i in range(len(data_46B)):
                for k in range(len(JDD_Minéraux_List)):
                    if JDD_Minéraux_List[k][1] == data_46B[i]:
                        data_46B1.append(data_46B[i])
                        for l in [0, 2, 3, 4, 5, 6]:
                            data_46B1.append(JDD_Minéraux_List[k][l])
            step, size = 7, 7
            JDD_46B_ = []
            for i in range(0, len(data_46B1), step):
                # slicing list
                JDD_46B_.append(data_46B1[i: i + size])
            DataSet_46B = pd.DataFrame(JDD_46B_,
                                       columns=[ 'Ref 46B','Date', 'K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)',
                                                'Na (cmol+/Kg)', 'Al (cmol+/Kg)'])

            return DataSet_46B

        ref_46B = ref_46B()

        def insert_46B_MDB():

            if ref_46B.empty:
                return None
            ca = certifi.where()
            client = MongoClient(
                "mongodb+srv://team_lotfi:teamLotfi@cluster0.zdz0hto.mongodb.net/?retryWrites=true&w=majority",
                tlsCAFile=ca)
            db = client.Echangeables  # use or create a database named db
            B46_collection = db.B46_collection  # use or create a collection named JDD46B_collection
            JDD_46B_Dict = ref_46B.to_dict(orient='records')
            for doc in JDD_46B_Dict:
                if not B46_collection.find_one(doc):
                    B46_collection.insert_one(doc)
            return B46_collection

        def recap_46B_MDB():
            ca = certifi.where()
            client = MongoClient(
                "mongodb+srv://team_lotfi:teamLotfi@cluster0.zdz0hto.mongodb.net/?retryWrites=true&w=majority",
                tlsCAFile=ca)
            db = client.Echangeables
            B46_collection = db.B46_collection
            # last_elt_46B = []
            mydoc = db.B46_collection.find().sort('_id', -1).limit(37)
            last_elt_B46 = []
            for x in mydoc:
                last_elt_B46.append(x)
            B46_last_37 = pd.DataFrame(last_elt_B46)
            B46_last_37 = B46_last_37.drop(['_id'], axis=1)
            return B46_last_37

        def Statistique_46B():
            recap_46B_MODB=recap_46B_MDB()

            # Calculer la moyenne et l'écart-type
            Moyenne_46B = []
            EcartType_46B = []
            for i in ['K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)', 'Na (cmol+/Kg)', 'Al (cmol+/Kg)']:
                Moyenne_46B.append(round(recap_46B_MODB[i].mean(), 5))
                EcartType_46B.append(round(recap_46B_MODB[i].std(), 5))

            # Calculer le coefficient de variation
            CoefV_46 = []
            for i, j in zip(Moyenne_46B, EcartType_46B):
                CoefV_46.append((j / i) * 100)

            # Ecart-type moyenne
            CoefV_46B_Moy_ = []
            Nb_46B = len(recap_46B_MODB)
            for j in EcartType_46B:
                CoefV_46B_Moy_.append(j / np.sqrt(Nb_46B))

            # calculer la limite de surveillance et d'action
            LS_46B_ = []
            LA_46B_ = []
            for j in CoefV_46:
                LS_46B_.append(2.03 * j)
                LA_46B_.append(2.72 * j)

            # Calculer le nombre
            NB_46B_ = []
            for j in ['K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)', 'Na (cmol+/Kg)', 'Al (cmol+/Kg)']:
                NB_46B_.append(len(recap_46B_MODB[j]))
            Date_Premier_Echantillon_=[]
            Date_Dernier_Echantillon_=[]
            for j in range(5):
                Date_Premier_Echantillon_.append(recap_46B_MODB['Date'].iloc[-1])
                Date_Dernier_Echantillon_.append(recap_46B_MODB['Date'].iloc[0])

            Statistiques_46B = [Moyenne_46B, EcartType_46B, CoefV_46, NB_46B_, Date_Premier_Echantillon_, Date_Dernier_Echantillon_, CoefV_46B_Moy_, LS_46B_, LA_46B_]
            DataSet_46B_Stats = pd.DataFrame(Statistiques_46B,
                                             columns=['K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)', 'Na (cmol+/Kg)','Al (cmol+/Kg)'])
            DataSet_46B_Stats.insert(0, 'Standars_Statistiques',['Moyenne', 'Ecart Type', 'Coefficient variation', 'Nb', 'Date Premier Echantillon', 'Date Dernier Echantillon','Ecart Type Moyenne','Limite Surveillance', 'Limite Action'])

            return (DataSet_46B_Stats,Statistiques_46B)



        def ref_ER():
            JDD_Minéraux_List = JDD_Minéraux.values.tolist()
            data_ER = []
            Echantillon = []
            for i in (JDD_Minéraux_List):
                Echantillon.append(i[1])
            for k in Echantillon:
                if k[0:2] == 'ER':
                    data_ER.append(k)
            data_ER1 = []
            for i in range(len(data_ER)):
                for k in range(len(JDD_Minéraux_List)):
                    if JDD_Minéraux_List[k][1] == data_ER[i]:
                        data_ER1.append(data_ER[i])
                        for l in [0, 2, 3, 4, 5, 6]:
                            data_ER1.append(JDD_Minéraux_List[k][l])
            step, size = 7, 7
            JDD_ER_ = []
            for i in range(0, len(data_ER1), step):
                # slicing list
                JDD_ER_.append(data_ER1[i: i + size])
            DataSet_ER = pd.DataFrame(JDD_ER_,
                                       columns=[ 'Ref ER','Date', 'K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)',
                                                'Na (cmol+/Kg)', 'Al (cmol+/Kg)'])

            return DataSet_ER

        ref_ER = ref_ER()

        def insert_ER_MDB():

            if ref_ER.empty:
                return None
            ca = certifi.where()
            client = MongoClient(
                "mongodb+srv://team_lotfi:teamLotfi@cluster0.zdz0hto.mongodb.net/?retryWrites=true&w=majority",
                tlsCAFile=ca)
            db = client.Echangeables  # use or create a database named db
            ER_collection = db.ER_collection  # use or create a collection named JDD46B_collection
            JDD_ER_Dict = ref_ER.to_dict(orient='records')
            for doc in JDD_ER_Dict:
                if not ER_collection.find_one(doc):
                    ER_collection.insert_one(doc)

            #JDDER_collection.insert_many(JDD_ER_Dict)
            return ER_collection

        def recap_ER_MDB():
            ca = certifi.where()
            client = MongoClient(
                "mongodb+srv://team_lotfi:teamLotfi@cluster0.zdz0hto.mongodb.net/?retryWrites=true&w=majority",
                tlsCAFile=ca)
            db = client.Echangeables
            ER_collection = db.ER_collection
            # last_elt_46B = []
            mydoc = db.ER_collection.find().sort('_id', -1).limit(37)
            last_elt_ER = []
            for x in mydoc:
                last_elt_ER.append(x)
            ER_last_37 = pd.DataFrame(last_elt_ER)
            ER_last_37 = ER_last_37.drop(['_id'], axis=1)
            return ER_last_37

        def Statistique_ER():
            recap_ER_MODB=recap_ER_MDB()
            #Date_Premier_Echantillon = recap_ER_MODB['Date'].iloc[-1]
            #Date_Dernier_Echantillon = recap_ER_MODB['Date'].iloc[0]
                        # Calculer la moyenne et l'écart-type
            Moyenne_ER = []
            EcartType_ER = []
            for i in ['K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)', 'Na (cmol+/Kg)', 'Al (cmol+/Kg)']:
                Moyenne_ER.append(round(recap_ER_MODB[i].mean(), 5))
                EcartType_ER.append(round(recap_ER_MODB[i].std(), 5))
            # Calculer le coefficient de variation
            CoefV_ER = []
            for i, j in zip(Moyenne_ER, EcartType_ER):
                CoefV_ER.append((j / i) * 100)
            # Ecart-type moyenne
            CoefV_ER_Moy_ = []
            Nb_ER = len(recap_ER_MODB)
            for j in EcartType_ER:
                CoefV_ER_Moy_.append(j / np.sqrt(Nb_ER))
            # calculer la limite de surveillance et d'action
            LS_ER_ = []
            LA_ER_ = []
            for j in CoefV_ER:
                LS_ER_.append(2.03 * j)
                LA_ER_.append(2.72 * j)

            # Calculer le nombre
            NB_ER_ = []
            for j in ['K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)', 'Na (cmol+/Kg)', 'Al (cmol+/Kg)']:
                NB_ER_.append(len(recap_ER_MODB[j]))
            Date_Premier_Echantillon_ = []
            Date_Dernier_Echantillon_ = []
            for j in range(5):
                Date_Premier_Echantillon_.append(recap_ER_MODB['Date'].iloc[-1])
                Date_Dernier_Echantillon_.append(recap_ER_MODB['Date'].iloc[0])
            Statistiques_ER = [Moyenne_ER, EcartType_ER, CoefV_ER, NB_ER_,Date_Premier_Echantillon_, Date_Dernier_Echantillon_, CoefV_ER_Moy_, LS_ER_, LA_ER_]
            DataSet_ER_Stats = pd.DataFrame(Statistiques_ER,columns=['K (cmol+/Kg)', 'Ca (cmol+/Kg)', 'Mg (cmol+/Kg)', 'Na (cmol+/Kg)','Al (cmol+/Kg)'])
            DataSet_ER_Stats.insert(0, 'Standars_Statistiques',['Moyenne', 'Ecart Type', 'Coefficient variation', 'Nb','Date Premier Echantillon', 'Date Dernier Echantillon', 'Ecart Type Moyenne','Limite Surveillance', 'Limite Action'])
            return (DataSet_ER_Stats,Statistiques_ER)

        statistique_ER, statistique_ER_list = Statistique_ER()
        statistique_46B, statistique_46B_list = Statistique_46B()


        #### Tracer Carte de controle du référentiel 46B

            #calcul_LSS_LSI_:
        def LSS_LSI_46B():
            LSS_46B_ = []
            LSI_46B_ = []
            for i, j in zip(statistique_46B_list[0], statistique_46B_list[7]):
                LSS_46B_.append(round(i * (1 + (j / 100)), 5))
                LSI_46B_.append(round(i * (1 - (j / 100)), 5))
            return (LSS_46B_, LSI_46B_)

        #Calcul de LAS et LAI
        def LAS_LAI_46B():
            LAS_46B_ = []
            LAI_46B_ = []
            for i, j in zip(statistique_46B_list[0], statistique_46B_list[8]):
                LAS_46B_.append(round(i * (1 + (j / 100)), 5))
                LAI_46B_.append(round(i * (1 - (j / 100)), 5))
            return (LAS_46B_, LAI_46B_)

        def standars_CC_K():
            LSS_46B,LSI_46B = LSS_LSI_46B()
            LAS_46B, LAI_46B = LAS_LAI_46B()
            B46_latest=recap_46B_MDB()
            x = list(B46_latest.index.values)
            B46_latest = B46_latest.assign(Index=x)
            B46_latest = B46_latest.assign(Moyenne=statistique_46B_list[0][0])
            B46_latest = B46_latest.assign(LSSupérieure=LSS_46B[0])
            B46_latest = B46_latest.assign(LSInférieure=LSI_46B[0])
            B46_latest = B46_latest.assign(LASupérieure=LAS_46B[0])
            B46_latest = B46_latest.assign(LAInférieure=LAI_46B[0])

            return B46_latest

        def standars_CC_Ca():
            LSS_46B, LSI_46B = LSS_LSI_46B()
            LAS_46B, LAI_46B = LAS_LAI_46B()
            B46_latest = recap_46B_MDB()
            x = list(B46_latest.index.values)
            B46_latest = B46_latest.assign(Index=x)
            B46_latest = B46_latest.assign(Moyenne=statistique_46B_list[0][1])
            B46_latest = B46_latest.assign(LSSupérieure=LSS_46B[1])
            B46_latest = B46_latest.assign(LSInférieure=LSI_46B[1])
            B46_latest = B46_latest.assign(LASupérieure=LAS_46B[1])
            B46_latest = B46_latest.assign(LAInférieure=LAI_46B[1])

            return B46_latest

        def standars_CC_Mg():
            LSS_46B, LSI_46B = LSS_LSI_46B()
            LAS_46B, LAI_46B = LAS_LAI_46B()
            B46_latest = recap_46B_MDB()
            x = list(B46_latest.index.values)
            B46_latest = B46_latest.assign(Index=x)
            B46_latest = B46_latest.assign(Moyenne=statistique_46B_list[0][2])
            B46_latest = B46_latest.assign(LSSupérieure=LSS_46B[2])
            B46_latest = B46_latest.assign(LSInférieure=LSI_46B[2])
            B46_latest = B46_latest.assign(LASupérieure=LAS_46B[2])
            B46_latest = B46_latest.assign(LAInférieure=LAI_46B[2])

            return B46_latest

        def standars_CC_Na():
            LSS_46B, LSI_46B = LSS_LSI_46B()
            LAS_46B, LAI_46B = LAS_LAI_46B()
            B46_latest = recap_46B_MDB()
            x = list(B46_latest.index.values)
            B46_latest = B46_latest.assign(Index=x)
            B46_latest = B46_latest.assign(Moyenne=statistique_46B_list[0][3])
            B46_latest = B46_latest.assign(LSSupérieure=LSS_46B[3])
            B46_latest = B46_latest.assign(LSInférieure=LSI_46B[3])
            B46_latest = B46_latest.assign(LASupérieure=LAS_46B[3])
            B46_latest = B46_latest.assign(LAInférieure=LAI_46B[3])

            return B46_latest

        def standars_CC_Al():
            LSS_46B, LSI_46B = LSS_LSI_46B()
            LAS_46B, LAI_46B = LAS_LAI_46B()
            B46_latest = recap_46B_MDB()
            x = list(B46_latest.index.values)
            B46_latest = B46_latest.assign(Index=x)
            B46_latest = B46_latest.assign(Moyenne=statistique_46B_list[0][4])
            B46_latest = B46_latest.assign(LSSupérieure=LSS_46B[4])
            B46_latest = B46_latest.assign(LSInférieure=LSI_46B[4])
            B46_latest = B46_latest.assign(LASupérieure=LAS_46B[4])
            B46_latest = B46_latest.assign(LAInférieure=LAI_46B[4])

            return B46_latest

        #### Tracer Carte de controle du référentiel 46B

            # calcul_LSS_LSI_:

        def LSS_LSI_ER():
            LSS_ER_ = []
            LSI_ER_ = []
            for i, j in zip(statistique_ER_list[0], statistique_ER_list[7]):
                LSS_ER_.append(round(i * (1 + (j / 100)), 5))
                LSI_ER_.append(round(i * (1 - (j / 100)), 5))
            return (LSS_ER_, LSI_ER_)

            # Calcul de LAS et LAI
        def LAS_LAI_ER():
            LAS_ER_ = []
            LAI_ER_ = []
            for i, j in zip(statistique_ER_list[0], statistique_ER_list[8]):
                LAS_ER_.append(round(i * (1 + (j / 100)), 5))
                LAI_ER_.append(round(i * (1 - (j / 100)), 5))
            return (LAS_ER_, LAI_ER_)

        def standars_CC_K_ER():
            LSS_ER, LSI_ER = LSS_LSI_ER()
            LAS_ER, LAI_ER = LAS_LAI_ER()
            ER_latest = recap_ER_MDB()
            x = list(ER_latest.index.values)
            ER_latest = ER_latest.assign(Index=x)
            ER_latest = ER_latest.assign(Moyenne=statistique_ER_list[0][0])
            ER_latest = ER_latest.assign(LSSupérieure=LSS_ER[0])
            ER_latest = ER_latest.assign(LSInférieure=LSI_ER[0])
            ER_latest = ER_latest.assign(LASupérieure=LAS_ER[0])
            ER_latest = ER_latest.assign(LAInférieure=LAI_ER[0])

            return ER_latest
        def standars_CC_Ca_ER():
            LSS_ER, LSI_ER = LSS_LSI_ER()
            LAS_ER, LAI_ER = LAS_LAI_ER()
            ER_latest = recap_ER_MDB()
            x = list(ER_latest.index.values)
            ER_latest = ER_latest.assign(Index=x)
            ER_latest = ER_latest.assign(Moyenne=statistique_ER_list[0][1])
            ER_latest = ER_latest.assign(LSSupérieure=LSS_ER[1])
            ER_latest = ER_latest.assign(LSInférieure=LSI_ER[1])
            ER_latest = ER_latest.assign(LASupérieure=LAS_ER[1])
            ER_latest = ER_latest.assign(LAInférieure=LAI_ER[1])

            return ER_latest
        def standars_CC_Mg_ER():
            LSS_ER, LSI_ER = LSS_LSI_ER()
            LAS_ER, LAI_ER = LAS_LAI_ER()
            ER_latest = recap_ER_MDB()
            x = list(ER_latest.index.values)
            ER_latest = ER_latest.assign(Index=x)
            ER_latest = ER_latest.assign(Moyenne=statistique_ER_list[0][2])
            ER_latest = ER_latest.assign(LSSupérieure=LSS_ER[2])
            ER_latest = ER_latest.assign(LSInférieure=LSI_ER[2])
            ER_latest = ER_latest.assign(LASupérieure=LAS_ER[2])
            ER_latest = ER_latest.assign(LAInférieure=LAI_ER[2])

            return ER_latest

        def standars_CC_Na_ER():
            LSS_ER, LSI_ER = LSS_LSI_ER()
            LAS_ER, LAI_ER = LAS_LAI_ER()
            ER_latest = recap_ER_MDB()
            x = list(ER_latest.index.values)
            ER_latest = ER_latest.assign(Index=x)
            ER_latest = ER_latest.assign(Moyenne=statistique_ER_list[0][3])
            ER_latest = ER_latest.assign(LSSupérieure=LSS_ER[3])
            ER_latest = ER_latest.assign(LSInférieure=LSI_ER[3])
            ER_latest = ER_latest.assign(LASupérieure=LAS_ER[3])
            ER_latest = ER_latest.assign(LAInférieure=LAI_ER[3])

            return ER_latest

        def standars_CC_Al_ER():
            LSS_ER, LSI_ER = LSS_LSI_ER()
            LAS_ER, LAI_ER = LAS_LAI_ER()
            ER_latest = recap_ER_MDB()
            x = list(ER_latest.index.values)
            ER_latest = ER_latest.assign(Index=x)
            ER_latest = ER_latest.assign(Moyenne=statistique_ER_list[0][4])
            ER_latest = ER_latest.assign(LSSupérieure=LSS_ER[4])
            ER_latest = ER_latest.assign(LSInférieure=LSI_ER[4])
            ER_latest = ER_latest.assign(LASupérieure=LAS_ER[4])
            ER_latest = ER_latest.assign(LAInférieure=LAI_ER[4])

            return ER_latest


        inserer_46B = insert_46B_MDB()
        inserer_ER = insert_ER_MDB()

        Standards_K=standars_CC_K()
        Standards_Ca = standars_CC_Ca()
        Standards_Mg = standars_CC_Mg()
        Standards_Na = standars_CC_Na()
        Standards_Al = standars_CC_Al()
        B46_latest = recap_46B_MDB()
        Standards_K_ER = standars_CC_K_ER()
        Standards_Ca_ER = standars_CC_Ca_ER()
        Standards_Mg_ER = standars_CC_Mg_ER()
        Standards_Na_ER = standars_CC_Na_ER()
        Standards_Al_ER = standars_CC_Al_ER()
        B46_latest_ER = recap_ER_MDB()

        st.title("Statistiques Descriptives")

        stat_col1, stat_col2, stat_col3 = st.columns([1, 1, 1])

        with stat_col1:
            st.title("")

        with stat_col2:
            image = Image.open('Statistique.png')
            st.image(image, use_column_width=True)

        with stat_col3:
            st.title("")

        if st.button("Matériel de Référence Interne 46B"):
            st.header(":blue[Matériel de Référence Interne : 46B]")
            st.write(pd.DataFrame({
                'Standars_Statistiques': statistique_46B['Standars_Statistiques'],
                'K (cmol+/Kg)': statistique_46B['K (cmol+/Kg)'],
                'Ca (cmol+/Kg)': statistique_46B['Ca (cmol+/Kg)'],
                'Mg (cmol+/Kg)': statistique_46B['Mg (cmol+/Kg)'],
                'Na (cmol+/Kg)': statistique_46B['Na (cmol+/Kg)'],
                'Al (cmol+/Kg)': statistique_46B['Al (cmol+/Kg)'],

            }))

        if st.button("Matériel de Référence Interne ER"):
            st.header(":blue[Matériel de Référence Interne : ER]")
            st.write(pd.DataFrame({
                'Standars_Statistiques': statistique_ER['Standars_Statistiques'],
                'K (cmol+/Kg)': statistique_ER['K (cmol+/Kg)'],
                'Ca (cmol+/Kg)': statistique_ER['Ca (cmol+/Kg)'],
                'Mg (cmol+/Kg)': statistique_ER['Mg (cmol+/Kg)'],
                'Na (cmol+/Kg)': statistique_ER['Na (cmol+/Kg)'],
                'Al (cmol+/Kg)': statistique_ER['Al (cmol+/Kg)'],

            }))

        st.title("Cartes de Contrôle")

        stat_col1, stat_col2, stat_col3 = st.columns([1, 1, 1])

        with stat_col1:
            st.title("")

        with stat_col2:
            image = Image.open('carte_controle.png')
            st.image(image, use_column_width=True)

        with stat_col3:
            st.title("")

        if st.button("Matériel de Référence Interne : 46B"):
            st.header("Base Echangeable : K (cmol+/Kg)")
            x = list(Standards_K.index.values)
            y1 = Standards_K['K (cmol+/Kg)']
            y2 = Standards_K['Moyenne']
            y3 = Standards_K['LSSupérieure']
            y4 = Standards_K['LSInférieure']
            y5 = Standards_K['LASupérieure']
            y6 = Standards_K['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="K (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

            st.header("Base Echangeable : Ca (cmol+/Kg)")
            x = list(Standards_Ca.index.values)
            y1 = Standards_Ca['Ca (cmol+/Kg)']
            y2 = Standards_Ca['Moyenne']
            y3 = Standards_Ca['LSSupérieure']
            y4 = Standards_Ca['LSInférieure']
            y5 = Standards_Ca['LASupérieure']
            y6 = Standards_Ca['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="Ca (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

            st.header("Base Echangeable : Mg (cmol+/Kg)")
            x = list(Standards_Mg.index.values)
            y1 = Standards_Mg['Mg (cmol+/Kg)']
            y2 = Standards_Mg['Moyenne']
            y3 = Standards_Mg['LSSupérieure']
            y4 = Standards_Mg['LSInférieure']
            y5 = Standards_Mg['LASupérieure']
            y6 = Standards_Mg['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="Mg (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

            st.header("Base Echangeable : Na (cmol+/Kg)")
            x = list(Standards_Na.index.values)
            y1 = Standards_Na['Na (cmol+/Kg)']
            y2 = Standards_Na['Moyenne']
            y3 = Standards_Na['LSSupérieure']
            y4 = Standards_Na['LSInférieure']
            y5 = Standards_Na['LASupérieure']
            y6 = Standards_Na['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="Na (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

            st.header("Base Echangeable : Al (cmol+/Kg)")
            x = list(Standards_Al.index.values)
            y1 = Standards_Al['Al (cmol+/Kg)']
            y2 = Standards_Al['Moyenne']
            y3 = Standards_Al['LSSupérieure']
            y4 = Standards_Al['LSInférieure']
            y5 = Standards_Al['LASupérieure']
            y6 = Standards_Al['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="Al (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

        if st.button("Matériel de Référence Interne : ER"):
            st.header("Base Echangeable : K (cmol+/Kg)")
            x = list(Standards_K_ER.index.values)
            y1 = Standards_K_ER['K (cmol+/Kg)']
            y2 = Standards_K_ER['Moyenne']
            y3 = Standards_K_ER['LSSupérieure']
            y4 = Standards_K_ER['LSInférieure']
            y5 = Standards_K_ER['LASupérieure']
            y6 = Standards_K_ER['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="K (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

            st.header("Base Echangeable : Ca (cmol+/Kg)")
            x = list(Standards_Ca_ER.index.values)
            y1 = Standards_Ca_ER['Ca (cmol+/Kg)']
            y2 = Standards_Ca_ER['Moyenne']
            y3 = Standards_Ca_ER['LSSupérieure']
            y4 = Standards_Ca_ER['LSInférieure']
            y5 = Standards_Ca_ER['LASupérieure']
            y6 = Standards_Ca_ER['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="Ca (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

            st.header("Base Echangeable : Mg (cmol+/Kg)")
            x = list(Standards_Mg_ER.index.values)
            y1 = Standards_Mg_ER['Mg (cmol+/Kg)']
            y2 = Standards_Mg_ER['Moyenne']
            y3 = Standards_Mg_ER['LSSupérieure']
            y4 = Standards_Mg_ER['LSInférieure']
            y5 = Standards_Mg_ER['LASupérieure']
            y6 = Standards_Mg_ER['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="Mg (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

            st.header("Base Echangeable : Na (cmol+/Kg)")
            x = list(Standards_Mg_ER.index.values)
            y1 = Standards_Na_ER['Na (cmol+/Kg)']
            y2 = Standards_Na_ER['Moyenne']
            y3 = Standards_Na_ER['LSSupérieure']
            y4 = Standards_Na_ER['LSInférieure']
            y5 = Standards_Na_ER['LASupérieure']
            y6 = Standards_Na_ER['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="Na (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)

            st.header("Base Echangeable : Al (cmol+/Kg)")
            x = list(Standards_Al_ER.index.values)
            y1 = Standards_Al_ER['Al (cmol+/Kg)']
            y2 = Standards_Al_ER['Moyenne']
            y3 = Standards_Al_ER['LSSupérieure']
            y4 = Standards_Al_ER['LSInférieure']
            y5 = Standards_Al_ER['LASupérieure']
            y6 = Standards_Al_ER['LAInférieure']
            plt.rcParams["figure.figsize"] = [16, 13]
            fig, ax = plt.subplots()
            ax.plot(x, y1, label="Al (cmol+/Kg)", color='k')
            plt.scatter(x, y1, color='r')
            # plt.scatter(B46_last_37.index,B46_last_37['K (cmol+/Kg)'])
            ax.plot(x, y2, label="Moyenne", color='g')
            ax.plot(x, y3, label="LSS", color='b')
            ax.plot(x, y4, label="LSI", color='b')
            ax.plot(x, y5, label="LAS", color='r')
            ax.plot(x, y6, label="LAI", color='r')
            ax.legend(loc='best')
            st.pyplot(fig)





if __name__ == '__main__':
    main()