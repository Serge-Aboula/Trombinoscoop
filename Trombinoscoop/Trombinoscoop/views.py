from datetime import datetime
from django.shortcuts import render, redirect
from django import forms
from django.http import HttpResponse, JsonResponse

from Trombinoscoop.models import Person, Student, Employee, Message
from Trombinoscoop.forms import LoginForm, StudentProfileForm, EmployeeProfileForm, addFriendForm

def index(request):
    return render(request, 'index.html')

def login(request):
    if not request.POST:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    
    form = LoginForm(request.POST)
    
    if not form.is_valid():
        return render(request, 'login.html', {'form': form})
    
    user_email = form.cleaned_data['email']
    logged_user = Person.objects.get(email=user_email)
    request.session['logged_user_id'] = logged_user.id
    
    return redirect('/welcome')

def register(request):
    if not request.GET or  not 'profileType' in request.GET:
        studentForm = StudentProfileForm(prefix='st')
        employeeForm = EmployeeProfileForm(prefix='em')
        return render(request, 'user_profile.html', {'studentForm': studentForm,
                                                     'employeeForm': employeeForm})
    
    studentForm = StudentProfileForm(prefix='st')
    employeeForm = EmployeeProfileForm(prefix='em')
    
    if request.GET['profileType'] == 'student':
        studentForm = StudentProfileForm(request.GET, prefix='st')
    
        if not studentForm.is_valid():
            return render(request, 'user_profile.html', {'studentForm': studentForm,
                                                         'employeeForm': employeeForm})
        
        studentForm.save()
        new_user = Person.objects.last()
        new_user.friends.add(new_user)
        #print(new_user)
        new_user.save()
        return redirect('/login')
    
    elif request.GET['profileType'] == 'employee':
        employeeForm = EmployeeProfileForm(request.GET, prefix='em')
    
        if not employeeForm.is_valid():
            return render(request, 'user_profile.html', {'employeeForm': employeeForm,
                                                         'studentForm': studentForm})
        
        employeeForm.save()
        new_user = Person.objects.last()
        new_user.friends.add(new_user)
        #print(new_user)
        new_user.save()
        return redirect('/login')

def get_logged_user_from_request(request):
    if not 'logged_user_id' in request.session:
        return None
    
    logged_user_id = request.session['logged_user_id']
    # On cherche un étudiant
    if len(Student.objects.filter(id=logged_user_id)) == 1:
        return Student.objects.get(id=logged_user_id)
    # On cherche un employé
    elif len(Employee.objects.filter(id=logged_user_id)) == 1:
        return Employee.objects.get(id=logged_user_id)
    # Si on n'a rien trouvé
    else:
        return None
   
def welcome(request):
    logged_user = get_logged_user_from_request(request) 
    
    if not logged_user:        
        return redirect('/login')
    
    return render(request, 'welcome.html', {"current_date_time": datetime.now, 'logged_user': logged_user})

def json_get_messages(request):
    logged_user = get_logged_user_from_request(request) 
    
    if not logged_user:        
        return redirect('/login')
    
    friendMessages = list(Message.objects.filter(
            author__friends=logged_user).values('author', 'content', 'publication_date'))#.filter(\
            #author__friends=logged_user).values('author', 'content', 'publication_date'))#.order_by('-publication_date')
    #print(friendMessages)
    for key in friendMessages:
        #print(key)
        #print(friendMessages) 
        #print(key['author'])
        msgAuthor = list(Person.objects.filter(id=key['author']).values('id', 'last_name', 'first_name'))
        key['author'] = msgAuthor
        #print(key['author'])
    
    if logged_user.person_type == 'student':
        logged_user = list(Student.objects.filter(id=logged_user.id).values('id', 'last_name', 'first_name'))
    else:
        logged_user = list(Employee.objects.filter(id=logged_user.id).values('id', 'last_name', 'first_name'))
    #print(logged_user)   
            
    return JsonResponse({"logged_user": logged_user,
                         "friendMessages": friendMessages
                        }, safe=False)

def json_get_friends(request):
    logged_user = get_logged_user_from_request(request) 
    
    if not logged_user:        
        return redirect('/login')
    
    friendsList = list(logged_user.friends.all().values('id', 'last_name', 'first_name'))
    #print(friendsList)
    #for elt in friendsList:
        #print(elt)   
    
    if logged_user.person_type == 'student':
        logged_user = list(Student.objects.filter(id=logged_user.id).values('id', 'last_name', 'first_name'))
    else:
        logged_user = list(Employee.objects.filter(id=logged_user.id).values('id', 'last_name', 'first_name'))
    #print(logged_user)   
            
    return JsonResponse({"logged_user": logged_user,
                         "friendsList": friendsList
                        }, safe=False)
    
def logout(request):
    request.session.flush()
    return redirect('/login')

def add_friend(request):
    # On récupère l'id de session 
    logged_user = get_logged_user_from_request(request)
    
    # Si l'utilisateur n'est pas authentifié
    if not logged_user:        
        return redirect('/login')
    
    # Si le formulaire n'est pas envoyé
    if not request.GET:
        form = addFriendForm()
        return render(request, 'add_friend.html', {'form': form})
    
    form = addFriendForm(request.GET)
    
    # Si le formulaire n'est pas valide
    if not form.is_valid():
        return render(request, 'add_friend.html', {'form': form})
    
    new_friend_email = form.cleaned_data['email']
    newFriend = Person.objects.get(email=new_friend_email)
    logged_user.friends.add(newFriend)
    logged_user.save()
    
    return redirect('/welcome')

def show_profile(request, id):
    # On récupère l'id de session 
    logged_user = get_logged_user_from_request(request)
    
    # Si l'utilisateur n'est pas authentifié
    if not logged_user:        
        return redirect('/login')    
    
    # if not 'userToShow' in request.GET or request.GET['userToShow'] == '':
    #     return render(request, 'show_profile.html', {'user_to_show': logged_user})
    
    # L'id de la personne dont on veut voir le profil est bien passé en paramètre 
    user_to_show_id = id #int(request.GET['userToShow'])
    person = Person.objects.filter(id=user_to_show_id)
    
    if  len(person) != 1:
        return render(request, 'show_profile.html', {'user_to_show': logged_user})
    
    user_to_show = None
    
    if not Student.objects.filter(id=user_to_show_id):
        user_to_show = Employee.objects.get(id=user_to_show_id)    
    else:
        user_to_show = Student.objects.get(id=user_to_show_id)
    
    return render(request, 'show_profile.html', {'user_to_show': user_to_show})

def modify_profile(request):    
    logged_user = get_logged_user_from_request(request)
    
    if not logged_user:        
        return redirect('/login')
    
    form = None
    
    if not request.GET:
        if type(logged_user) == Student:
            form = StudentProfileForm(instance=logged_user)
        else:
            form = EmployeeProfileForm(instance=logged_user)
        
        return render(request, 'modify_profile.html', {'form': form})
    
    if type(logged_user) == Student:
        form = StudentProfileForm(request.GET, instance=logged_user)
    else:
        form = EmployeeProfileForm(request.GET, instance=logged_user)
    #print(type(logged_user) == Student)
    #print(form.is_valid())
    if not form.is_valid():
        #print('Formulaire non valide !')    
        #print(form)    
        return render(request, 'modify_profile.html', {'form': form}) 

    form.save()
    return redirect('/welcome')
    #return render(request, 'modify_profile.html', {'form': form}) # Génère une erreur !

def ajax_check_email_field(request):
    html_to_return = ''
    if 'value' in request.GET:
        field = forms.EmailField()
        try:
            field.clean(request.GET['value'])
        except forms.ValidationError as ve:
            html_to_return = '<ul class="errorlist">'
            for message in ve.messages:
                html_to_return += '<li>' + message + '</li>'
            html_to_return += '<ul>'
        
        if not html_to_return:
            if len(Person.objects.filter(email=request.GET['value'])) >= 1:
                html_to_return = '<ul class="errorlist">'
                html_to_return += '<li>Cette adresse est déjà utilisée !</li>'
                html_to_return += '<ul>'
    return HttpResponse(html_to_return)

def ajax_add_friend(request):
    html_to_return = ''
    logged_user = get_logged_user_from_request(request)
    if logged_user:        
        new_friend_email = ''
        if 'newFriendEmail' in request.GET:            
            new_friend_email = request.GET['newFriendEmail']
            if len(Person.objects.filter(email=new_friend_email)) == 1:
                new_friend = Person.objects.get(email=new_friend_email)
                if not logged_user.friends.filter(id=new_friend.id).exists():
                    logged_user.friends.add(new_friend)
                    logged_user.save()
                    html_to_return = '<li><a href="{% url ' + "'show_profile' " + str(new_friend.id) +' %}">'
                    html_to_return += new_friend.first_name + ' ' + new_friend.last_name
                    html_to_return += '</a></li>'        
    return HttpResponse(html_to_return)

def ajax_publish_msg(request):
    logged_user = get_logged_user_from_request(request)
    html_to_return = ''
    if logged_user:
        if 'newMessage' in request.GET and request.GET['newMessage'] != '': 
            newMessage = Message(author=logged_user,
                                 content=request.GET['newMessage'],
                                 publication_date=datetime.today())
            newMessage.save()
            html_to_return = 'ok'        
    return HttpResponse(html_to_return)
    
# def login(request):
#     # Teste si le formulaire a été envoyé
#     if not request.POST:
#         # Le formulaire n'a pas été envoyé
#         return render(request, 'login.html')
    
#     # Teste si les paramètres attendus ont été transmis
#     if 'email' not in request.POST or 'password' not in request.POST:
#         error = "Veuillez entrer un email et un mot de passe."
#         return render(request, 'login.html', {'error': error})
    
#     email = request.POST['email']
#     password = request.POST['password']
    
#     #Teste si le mot de passe est le bon
#     if password != '1' or email != 'a@b.c':
#        error = "Email ou mot de passe invalide"
#        return render(request, 'login.html', {'error': error}) 
    
#     # Tout est bon on va à la page d'accueil
#     return redirect('/welcome')
