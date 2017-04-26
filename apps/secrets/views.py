from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.db.models import Count
from .models import User, Secret, Like

def index(request):
    return render(request, 'secrets/index.html')

def register(request):
    if request.method == 'POST':
        data = {
        'fnom': request.POST['first_name'],
        'lnom': request.POST['last_name'],
        'e_address': request.POST['email'],
        'pass_word': request.POST['password'],
        'confirm_pass_word': request.POST['pw_confirm'],
        }
        new_user = User.objects.reg(data)



        print new_user
        if new_user['error_list']:
            for error in new_user['error_list']:
                messages.add_message(request, messages.ERROR, error)
            return redirect('/')
        else:
            request.session['user_id'] = new_user['new'].id
            request.session['user_name'] = new_user['new'].first_name
            return redirect('/secrets')

def login(request):
    if request.method == 'POST':
        print request.POST
        data = {
        'e_mail':request.POST['email'],
        'p_word':request.POST['password']
        }
        a_user = User.objects.log(data)
        if a_user['list_errors']:
            for error in a_user['list_errors']:
                messages.add_message(request, messages.ERROR, error)
            return redirect('/')
        else:
            request.session['user_id'] = a_user['logged_user'].id
            request.session['user_name'] = a_user['logged_user'].first_name
            return redirect('/secrets')

def secrets(request):
	current_user = User.objects.get(id = request.session['user_id'])
	all_secrets = Secret.objects.all().order_by('-created_at')[:3]
	secrets_list = []
	for secret in all_secrets:
		secret.liked = True
		secret.num_likes = Like.objects.filter(secret = secret).count()
		try:
			Like.objects.get(user = current_user, secret = secret)
		except:
			secret.liked = False
		secrets_list.append(secret)
	context={
	'secrets': secrets_list
	}
	return render(request, 'secrets/secrets.html', context)

def popular_secrets(request):
    current_user = User.objects.get(id = request.session['user_id'])
    all_secrets = Secret.objects.annotate(num_likes = Count('secret_likes')).order_by('-num_likes')
    secrets_list = []
    for secret in all_secrets:
        secret.liked = True
        secret.num_likes = Like.objects.filter(secret = secret).count()
        try:
            Like.objects.get(user = current_user, secret = secret)
        except:
            secret.liked = False
        secrets_list.append(secret)
    context = {
    'secrets': secrets_list
    }
    return render(request, 'secrets/top_secrets.html', context)

def new_secret(request):
    if request.method == 'POST':
        current_user = User.objects.get(id = request.session['user_id'])
        a_secret = Secret.objects.create(content = request.POST['content'], user = current_user)
    return redirect('/secrets')

def add_like(request, secret_id):
	a_secret = Secret.objects.get(id = secret_id)
	a_user = User.objects.get(id = request.session['user_id'])
	Like.objects.create(secret = a_secret, user = a_user)
	return redirect('/secrets')

def destroy_secret(request, secret_id):
    if request.method == 'POST':
        a_secret = Secret.objects.get(id = secret_id)
        if a_secret.user.id == request.session['user_id']:
            a_secret.delete()
        else:
            messages.add_message(request, messages.ERROR, "You ain't allowed to do that, son")
    return redirect('/secrets')
