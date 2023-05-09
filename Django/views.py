from django.http import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.template import loader
from predict import get_ner_predictions, get_re_predictions
from utils import display_ehr, get_long_relation_table, display_knowledge_graph, get_relation_table
from nltk import sent_tokenize

class NERTask:
    def __init__(self, ehr_text: str, model_choice: str):
        self.ehr_text = ehr_text
        self.model_choice = model_choice
dic = {'admin':"123"}
def judge(request):
    error={}
    if request.method=='POST':
        data=request.POST
        # print(data)
        account = data['account']
        pwd = data['pwd']
        print(1)
        if account in dic:
            print(2)
            if dic[account] == pwd:
                print(3)
                return redirect("ehr/")
            else:
                error['tip'] = "没有账号或密码错误！"
        else:
            error['tip'] = "没有账号或密码错误！"
    return redirect("/",error)


def login(request):
    error={}
    if request.method=='POST':
        data=request.POST
        print(data)
        account = data['account']
        pwd = data['pwd']
        # print(1)
        if account in dic:
            # print(2)
            if dic[account] == pwd:
                # print(3)
                return redirect("ehr/")
            else:
                error['tip'] = "没有账号或密码错误！"
        else:
            error['tip'] = "没有账号或密码错误！"
    return render(request,"login.html",error)

def register(request):
    success={}
    if request.method =="POST":
        data=request.POST
        dic[data["account"]]=data["pwd"]
        success["tip"]="添加成功！"
    return render(request,"register.html",success)

@csrf_exempt
def get_ehr_predictions(request):
    """Request EHR text data and the model choice for NER Task"""
    get_token(request)
    return render(request,"ehr.html")

def back(request):
    get_token(request)
    if request.method=="POST":
        dic={}
        for i in request.POST.keys():
            dic=eval(i)
        ner_input = NERTask(ehr_text=(dic['ehr_text']), model_choice=dic["model_choice"])
        ner_predictions = get_ner_predictions(
            ehr_record=ner_input.ehr_text,
            model_name=ner_input.model_choice,)

        re_predictions = get_re_predictions(ner_predictions)
        relation_table = get_long_relation_table(re_predictions.relations)

        html_ner = display_ehr(
            text=ner_input.ehr_text,
            entities=ner_predictions.get_entities(),
            relations=re_predictions.relations,
            return_html=True)

        graph_img = display_knowledge_graph(relation_table, return_html=True)

        if len(relation_table) > 0:
            relation_table_html = get_relation_table(relation_table)
        else:
            relation_table_html = "<p>No relations found</p>"

        if graph_img is None:
            graph_img = "<p>No Relation found!</p>"

        data = {'tagged_text': html_ner, 're_table': relation_table_html, 'graph': graph_img}
        # data = {'tagged_text': 1, 're_table': 2, 'graph': 3}
        return JsonResponse(data, status=200)
    else:
        return HttpResponse("error")
    

def get_sample_ehr(request):
    """Returns a sample EHR record"""
    with open("sample_ehr/104788.txt") as f:
        SAMPLE_EHR = f.read()
    context = {'data': SAMPLE_EHR}
    return JsonResponse(context, status=200)
