from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from models import Pays, Rencontre, Member, Pronostic, Tag
from django.template import loader
from django.http import Http404
from django.views import generic
from django.core.urlresolvers import reverse
from django.core import serializers
# Create your views here.


def home(request):
    user = get_object_or_404(Member, pk=request.session['member_id'])
    latest_rencontre_list = Rencontre.objects.order_by('-date')[:5]
    latest_rencontre_date = sorted(set(map(lambda r: r.date ,latest_rencontre_list)))
    
    pronostics = Pronostic.objects.filter(member__exact = user).all()
    
    latest_rencontre_date = set(map(lambda r: r.date ,latest_rencontre_list))
    
    
    
    context = {
        'user': user,
        'username' : request.session.get('username', None),
        'latest_rencontre_list' : latest_rencontre_list,
        'latest_rencontre_date': latest_rencontre_date,
        'pronostics':pronostics,
        #'temp':temp,
    }
    return render(request, 'euro/home.html', context)


def index(request):
    
    try :
        user = Member.objects.filter(pk=request.session['member_id']).get()
    except (KeyError, Member.DoesNotExist ) :
        user = None
        
    latest_rencontre_list = Tag.objects.all()
    pronostics = Pronostic.objects.filter(member__exact = user).all()
    context = {
        'latest_rencontre_list': latest_rencontre_list,
        'username' : request.session.get('username', None),
        'pronostics':pronostics,
    }
    return render(request, 'euro/index.html', context)


def next_matchs(request):
    try :
        user = Member.objects.filter(pk=request.session['member_id']).get()
    except (KeyError, Member.DoesNotExist ) :
        user = None
    
    latest_rencontre_list = Rencontre.objects.order_by('-date')[:15]
    latest_rencontre_date = sorted(set(map(lambda r: r.date ,latest_rencontre_list)))
    pronostics = Pronostic.objects.filter(member__exact = user).all()
    context = {
        'latest_rencontre_list': latest_rencontre_list,
        'latest_rencontre_date': latest_rencontre_date,
        'username' : request.session.get('username', None),
        'pronostics':pronostics,
    }
    return render(request, 'euro/nexts.html', context)



def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def detail(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def register(request):
    newMember = Member()
    newMember.username = request.POST['username']
    newMember.password = request.POST['password']
    newMember.email = request.POST['email']
    newMember.save()
    request.session['member_id'] = newMember.id
    request.session['username'] = newMember.username
    return HttpResponseRedirect(reverse('euro:index'))

def check_login(request):
    try :
        m = Member.objects.get(username=request.POST['username'])
    except (KeyError, Member.DoesNotExist) :
            return JsonResponse({'reason' : 'User doesn\'t exists.'})
    else :
        if m.password == request.POST['password']:
            request.session['member_id'] = m.id
            request.session['username'] = m.username
            return JsonResponse({'success' : '/success'})
        else:
            return JsonResponse({'reason' : 'Your username and password didn\'t match.'})

def save(request):
    try :
        user = Member.objects.filter(pk=request.session['member_id']).get()
        score1 = {}
        score2 = {}
        res =''
        for item in request.POST.items():
            #res += 'item '+ str(item) +' :'
            if (item[0].find('score')>-1 and item[1] != ''):
                match = item[0].split('_')[1]
                score = item[1]
                if (int(item[0].split('_')[2]) == 1):
                    score1[match] = score
                else:
                    score2[match] = score
        
        for item in score1.items():
            if (score2[item[0]]):
                p, created = Pronostic.objects.filter(match__exact=item[0]).filter(member__exact=user).get_or_create(
                    member=user,
                    match=Rencontre.objects.get(pk=item[0])
                )
                p.score1 = score1[item[0]]
                p.score2 = score2[item[0]]
                p.save()
                    
        return JsonResponse({'success' : 'success'})        
        
    except (KeyError, Member.DoesNotExist ) :
        return JsonResponse({'reason' : 'User doesn\'t exists.'})
    


def login(request):
    try :
        m = Member.objects.get(username=request.POST['username'])
    except (KeyError, Member.DoesNotExist) :
        return HttpResponse("Your username and password didn't match.")
    else :
        if m.password == request.POST['password']:
            request.session['member_id'] = m.id
            request.session['username'] = m.username
            return HttpResponseRedirect(reverse('euro:index'))
        else:
            return HttpResponse("Your username and password didn't match.")

def logout(request):
    try:
        del request.session['member_id']
        del request.session['username']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('euro:index'))
