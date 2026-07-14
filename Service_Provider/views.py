
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse


import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

from nltk.tokenize import word_tokenize
import string
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet') 
nltk.download('omw-1.4')
from nltk.corpus import stopwords

# Create your views here.
from Remote_User.models import ClientRegister_Model,cyber_threat_identification,detection_ratio,detection_accuracy

from django.core.cache import cache



def serviceproviderlogin(request):
    if request.method  == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password =="Admin":
            detection_accuracy.objects.all().delete()
            return redirect('View_Remote_Users')

    return render(request,'SProvider/serviceproviderlogin.html')


def View_Predicted_Cyber_Threat_Identification_Type_Ratio(request):
    # Clear previous records
    detection_ratio.objects.all().delete()

    total_count = cyber_threat_identification.objects.count()
    if total_count == 0:
        # No data to show
        return render(request, 'SProvider/View_Predicted_Cyber_Threat_Identification_Type_Ratio.html', {'objs': []})

    # Define keywords (exact phrase might not match; use icontains)
    threat_keyword = 'Adware or Keyloggers'
    no_threat_keyword = 'No Cyber Threat Found'

    # Count threat using icontains for flexibility
    threat_count = cyber_threat_identification.objects.filter(Prediction__icontains=threat_keyword).count()
    no_threat_count = cyber_threat_identification.objects.filter(Prediction__icontains=no_threat_keyword).count()

    # Calculate ratios
    print(threat_keyword)
    threat_ratio = (threat_count / total_count) * 100
    print(threat_ratio )
    print(no_threat_keyword)
    no_threat_ratio = (no_threat_count / total_count) * 100
    print(no_threat_ratio )

    # Save both ratios regardless if zero or not
    detection_ratio.objects.create(names='Cyber Threat Found - Adware or Keyloggers', ratio=threat_ratio)
  
    detection_ratio.objects.create(names='No Cyber Threat Found', ratio=no_threat_ratio)
    

    # Fetch all saved ratios for template
    objs = detection_ratio.objects.all()
    return render(request, 'SProvider/View_Predicted_Cyber_Threat_Identification_Type_Ratio.html', {'objs': objs})

def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def View_Predicted_Cyber_Threat_Identification_Type(request):
    obj =cyber_threat_identification.objects.all()
    return render(request, 'SProvider/View_Predicted_Cyber_Threat_Identification_Type.html', {'list_objects': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Predicted_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Predicted_Datasets.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = cyber_threat_identification.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:

        row_num = row_num + 1

        ws.write(row_num, 0, my_row.fid, font_style)
        ws.write(row_num, 1, my_row.tweet_text, font_style)
        ws.write(row_num, 2, my_row.timestamp, font_style)
        ws.write(row_num, 3, my_row.source, font_style)
        ws.write(row_num, 4, my_row.symbols, font_style)
        ws.write(row_num, 5, my_row.company_names, font_style)
        ws.write(row_num, 6, my_row.url, font_style)
        ws.write(row_num, 7, my_row.source_ip, font_style)
        ws.write(row_num, 8, my_row.protocol, font_style)
        ws.write(row_num, 9, my_row.dest_ip, font_style)
        ws.write(row_num, 10, my_row.Prediction, font_style)

    wb.save(response)
    return response

def train_model(request):
    detection_accuracy.objects.all().delete()

    df = pd.read_csv('Datasets.csv',encoding='latin-1')

    # data under nlp
    print("Data Processing Under Natural Language Processing (NLP)")
    data = []
    Labels = []
    # Data Processing Under Natural Language Processing (NLP)
    for row in df["tweet_text"]:
        # tokenize words
        words = word_tokenize(row)
        # remove punctuations
        clean_words = [word.lower() for word in words if word not in set(string.punctuation)]
        # remove stop words
        english_stops = set(stopwords.words('english'))
        characters_to_remove = ["''", '``', "rt", "https", "â€™", "â€œ", "â€", "\u200b", "--", "n't", "'s",
                                "...",
                                "//t.c"]
        clean_words = [word for word in clean_words if word not in english_stops]
        clean_words = [word for word in clean_words if word not in set(characters_to_remove)]
        # Lematise words
        wordnet_lemmatizer = WordNetLemmatizer()
        lemma_list = [wordnet_lemmatizer.lemmatize(word) for word in clean_words]
        data.append(lemma_list)

    def apply_results(label):
        if (label == 0):
            return 0  # No Threat
        elif (label == 1):
            return 1  # Threat

    df['results'] = df['Label'].apply(apply_results)

    X = df['tweet_text']
    y = df['results']

    print("Tweet Desc")
    print(X)
    print("Results")
    print(y)

    cv = CountVectorizer()
    X = cv.fit_transform(X)

    models = []
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
    X_train.shape, X_test.shape, y_train.shape

    print("Convolutional Neural Network--CNN")
    from sklearn.neural_network import MLPClassifier
    mlpc = MLPClassifier().fit(X_train, y_train)
    y_pred = mlpc.predict(X_test)
    testscore_mlpc = accuracy_score(y_test, y_pred)
    accuracy_score(y_test, y_pred)
    print(accuracy_score(y_test, y_pred))
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    models.append(('MLPClassifier', mlpc))
    detection_accuracy.objects.create(names="Convolutional Neural Network--CNN",
                                      ratio=accuracy_score(y_test, y_pred) * 100)

    print("Extra Tree Classifier")
    from sklearn.tree import ExtraTreeClassifier
    etc_clf = ExtraTreeClassifier()
    etc_clf.fit(X_train, y_train)
    etcpredict = etc_clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, etcpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, etcpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, etcpredict))
    models.append(('RandomForestClassifier', etc_clf))
    detection_accuracy.objects.create(names="Extra Tree Classifier", ratio=accuracy_score(y_test, etcpredict) * 100)

    # SVM Model
    print("SVM")
    from sklearn import svm
    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    models.append(('svm', lin_clf))
    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

    print("Logistic Regression")

    from sklearn.linear_model import LogisticRegression
    reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    models.append(('logistic', reg))
    detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)


    print("Gradient Boosting Classifier")

    from sklearn.ensemble import GradientBoostingClassifier
    clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0).fit(
        X_train,
        y_train)
    clfpredict = clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, clfpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, clfpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, clfpredict))
    models.append(('GradientBoostingClassifier', clf))
    detection_accuracy.objects.create(names="Gradient Boosting Classifier",
                                      ratio=accuracy_score(y_test, clfpredict) * 100)




    csv_format = 'Results.csv'
    df.to_csv(csv_format, index=False)
    df.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request,'SProvider/train_model.html', {'objs': obj})