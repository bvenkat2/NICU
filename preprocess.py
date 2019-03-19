import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import time
from datetime import date, timedelta
from sklearn import tree

original_data = pd.ExcelFile("BIC1038Results_DEID.xlsx")
nicustay = pd.read_excel(original_data,"NICU Stay")
labs1 = pd.read_excel(original_data,"Labs1")
labs2 = pd.read_excel(original_data,"Labs2")
problem_list = pd.read_excel(original_data,"ProblemList")
diagnoses = pd.read_excel(original_data,"Diagnoses")
#


#Ask Dr. Fung about correct way to handle this
# labs1 = labs1.replace("UnableToReport", np.nan)

def oldestDate():
    tDate = nicustay["NICU_START_DT_TM"][0]
    for date in nicustay["NICU_START_DT_TM"]:
        if type(date) == type(tDate) and date<tDate:
            tDate = date
    print("Oldest Date: ",tDate)


def newestDate():
    tDate = nicustay["NICU_START_DT_TM"][0]
    for date in nicustay["NICU_START_DT_TM"]:
        if type(date) == type(tDate) and date>tDate:
            tDate = date
        elif type(date) != type(date):
            print(date)
    print("Newest Date: ",tDate)

oldestDate()
newestDate()
def test():
    for id, lab in zip(labs1["PT_ID"],labs1["RESULT_VAL"]):
        if(id == 2747):
            print(id, lab)
# test()
def positivePatients():
    posCodes = ["ICD10-CM!A04.7", "ICD10-CM!K52.1", "ICD10-CM!K52.89", "ICD10-CM!K55.069",
                "ICD10-CM!K55.30", "ICD10-CM!K55.31", "ICD10-CM!K55.32", "ICD10-CM!K55.33",
                "ICD10-CM!K65.9"]
    idList = set([])
    for code in posCodes:
        con = diagnoses["CONCEPT_CKI"].str.contains(code)
        for id, check in zip(diagnoses["PT_ID"], con):
            if check:
                idList.add(id)
    return idList

def labsList():
    list = set([])
    for a in labs1["LAB"]:
        list.add(a)
    for b in labs2["LAB"]:
        list.add(b)
    print(list)
    return list
# labsList()

def inputFeatures():
    labs = list(labsList())
    featureMap = defaultdict(list)
    for id, lab, value, date in zip(labs1["PT_ID"],labs1["LAB"],labs1["RESULT_VAL"],labs1["CLINSIG_UPDT_DT_TM"]):
        if featureMap.get(id) is None:
            featureMap[id] = [None] * (len(labs) + 1)
            featureMap[id][labs.index(lab)] = (value, date)
        elif featureMap[id][labs.index(lab)] is None:
            featureMap[id][labs.index(lab)] = (value,date)
        elif featureMap[id][labs.index(lab)][1] < date:
            featureMap[id][labs.index(lab)] = (value,date)
    nMap = defaultdict(list)
    for a in featureMap:
            nMap[a] = [x[0] if x is not None else -1 for x in featureMap[a]]

    return nMap


# inputFeatures()

def runModel():
    map = inputFeatures()
    posCodes = positivePatients()
    y = [1 if x in posCodes else 0 for x in map]
    x = list(map.values())
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(x, y)

# runModel()

def inputFeatures():
    rdiag = recentDiagnosis()
    feature = pd.Series([])


def recentDiagnosis():
    map = dict({})
    for id, date, code in zip(diagnoses["PT_ID"],diagnoses["BEG_EFFECTIVE_DT_TM"],diagnoses["CONCEPT_CKI"]):
        var = map.get(id)
        if var is None:
            map[id] = (date, code)
        elif map[id][0]>date:
            map[id] = (date,code)
    return map
# recentDiagnosis()


# positivePatients()


def twoWeekLabs():
    ids = diagnoses["PT_ID"]
    codes = diagnoses["CONCEPT_CKI"]
    date = diagnoses["BEG_EFFECTIVE_DT_TM"]
    # df = pd.DataFrame([ids, codes, date], columns=['id', 'code', 'date'])
    df = pd.DataFrame({'id': ids, 'code': codes, 'date': date})

    # td1 = pd.Timedelta('14 days 0 hours 0 seconds')
    #
    allLabs = pd.concat([labs1,labs2])
    #
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by=['date'])
    #

    # print(df)
    # df.head()
    allLabs["CLINSIG_UPDT_DT_TM"] = pd.to_datetime(allLabs["CLINSIG_UPDT_DT_TM"])
    d = df['date'][0]
    # m = defaultdict(list)
    delta = timedelta(days=14)
    for dDate, dPt, dCode in zip(df['date'], df['id'], df['code']):
            for lPt, lDate, visID, name in zip(allLabs["PT_ID"], allLabs["CLINSIG_UPDT_DT_TM"], allLabs["VIS_ID"], allLabs["LAB"]):
                if dPt == lPt:
                    # recentLabMap[dCode].append(visID)
                    if(dDate-lDate < delta) and (lDate>d):
                        # m[dPt].append([dCode, visID])
                        # print(visID)
                        print(dPt, dCode, name, lDate, dDate)
                d = dDate
                    # print(dCode,dDate, lDate)
    # print(diagnosisDateMap)
    # print(recentLabMap)

    # print(m)
    # print(len(m))

def test():
    allLabs = pd.concat([labs1,labs2])
    print(diagnoses["BEG_EFFECTIVE_DT_TM"]-allLabs["CLINSIG_UPDT_DT_TM"])
def listDiagnosisCodes():
    print("List of diagnoses and codes")
    codes = pd.Series(diagnoses["CONCEPT_CKI"])
    # print(codes)
    shortened_codes = codes.apply(lambda x:  x[(x.find('!')+1):])
    # shortened_codes = codes

    code_map = {}

    for a, b in zip(shortened_codes, diagnoses["SOURCE_STRING"]):
        code_map[a] = b

    shortened_codes = shortened_codes.sort_values().unique()

    for val in shortened_codes:
        print(val + " " +code_map[val])
    print("Number of distinct codes:")
    print(len(shortened_codes))

def listProblemCodes():
    print("List of problems and codes")
    codes = pd.Series(problem_list["CONCEPT_CKI"])
    # print(codes)
    shortened_codes = codes.apply(lambda x:  x[(x.find('!')+1):])
    # shortened_codes = codes

    code_map = {}

    for a, b in zip(shortened_codes, problem_list["SOURCE_STRING"]):
        code_map[a] = b

    shortened_codes = shortened_codes.sort_values().unique()

    for val in shortened_codes:
        print(val,code_map[val])
    print("Number of distinct codes:")
    print(len(shortened_codes))



# listProblemCodes()
# listDiagnosisCodes()
def findPatientLabs():
    print(labs1["PT_ID"].value_counts()[:25])
def numLabsPerPatient():
    lab1_pt_counts = (labs1["PT_ID"].value_counts())
    lab2_pt_counts = labs2["PT_ID"].value_counts()
    # print(lab1_pt_counts)
    print("Statistics about Number of patient visits")
    print("Lab 1 Patient Visit Statistics: ")
    print(lab1_pt_counts.describe())
    print("Lab 2 Patient Visit Statistics: ")
    print(lab2_pt_counts.describe())
    # print(labs1["PT_ID"].value_counts() + labs2["PT_ID"].value_counts())
    print("\n")


def listDiseases():
    print("List of Diseases")
    arr = set([])
    for diag in diagnoses["SOURCE_STRING"]:
            arr.add(diag)
    print(arr)
    print("\n")


def problemMap():
    map = defaultdict(list)
    for pt, problem in zip(problem_list["PT_ID"], problem_list["SOURCE_STRING"]):
        if problem not in map[pt]:
            map[pt].append(problem)
    print("Most common problems")
    keys = list(map.keys())
    for i in range(25):
        print(keys[i],map[keys[i]])
    print("\n")


def diagnosisMap():
    map = defaultdict(list)
    for pt, diagnosis, date in zip(diagnoses["PT_ID"], diagnoses["SOURCE_STRING"]):
        if diagnosis not in map[pt]:
            map[pt].append(diagnosis)
    print("List of patient IDs and their cooresponding diagnoses")
    for key in map:
        print(str(key),map[key])
    print("\n")

def diagnosisCounts():
    # print(diagnoses["SOURCE_STRING"])
    # print(diagnoses["SOURCE_STRING"].value_counts())
    print("Most common diagnoses:")
    print(diagnoses["SOURCE_STRING"].value_counts()[:25])
    print("\n")
    # plt.title("Diagnoses")
    # plt.show()
    #
    # print(diagnoses["SOURCE_STRING"].describe())


def labStatsAndGraphs():
    lab1_data = labs1["LAB"]
    # preprocess(labs1["RESULT_VAL"])
    labs = []
    ind = []
    count = 0
    for a in lab1_data:
        if(labs.__contains__(a) == False):
            labs.append(a)
            ind.append(count)
        count = count + 1
    count = 0
    possible_values = []
    inside_array = []
    print(labs)
    print("\n")
    # print(ind)
    #
    checkUnits = False
    for a in range(len(ind) - 1):
        arr = []
        if labs1["UNITS"][ind[a + 1] + 1] == " ":
            checkUnits = True
        for v in range(ind[a + 1], ind[a + 2]):
            arr.append(labs1["RESULT_VAL"][v])
        # print(arr)
        arr = pd.Series(arr)
        plt.title(labs[a + 1])
        if checkUnits:
            arr.value_counts()[:20].plot(kind='barh')
            # plt.xticks(arr,set)
            plt.xlabel("Counts")
            # plt.show()
        else:
            arr.value_counts()[:20].plot(kind='barh')
            plt.ylabel(labs1["UNITS"][ind[a + 1] + 1])
            plt.xlabel("Counts")
            # plt.show()
        checkUnits = False
        plt.savefig(labs[a + 1] + ".png")
        print("\n" + labs[a + 1] + ": ")
        print(arr.describe())
        print("\n")

def totalNumPatients():
    group1= set(labs1["PT_ID"])
    group2 = set(labs2["PT_ID"])
    combinedPatients = group1 | group2
    print("Total number of Patients: ")
    print(len(combinedPatients))
    print("\n")




# problemMap()
# diagnosisCounts()
# numLabsPerPatient()
# totalNumPatients()
# labStatsAndGraphs()
# diagnosisMap()
# listDiseases()
# findPatientLabs()
# twoWeekLabs()
# twoWeekLabs()

