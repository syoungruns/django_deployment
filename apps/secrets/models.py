from __future__ import unicode_literals

from django.db import models

# Create your models here.

import re, bcrypt, datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class UserManager(models.Manager):
	def reg(self, data):
		"""
		data == context = {
			'fnom': request.POST['first_name'],
			'lnom': request.POST['last_name'],
			'e_address': request.POST['email'],
			'pass_word': request.POST['password'],
			'confirm_pass_word': request.POST['confirm'],
			'dob': request.POST['birthdate']
		} (being sent from views when we call the function)
		"""
		errors = [] #show user all errors at once... eventually
		#check that first and last name have at least two characters
		# and are both all letters (no numbers!)
		if len(data['fnom']) < 2:
			errors.append("First name must be at least two characters long.")
		if not data['fnom'].isalpha():
			errors.append("First name may only be letters.")
		if len(data['lnom']) < 2:
			errors.append("Last name must be at least two characters long.")
		if not data['lnom'].isalpha():
			errors.append("Last name may only be letters.")
		# check that email is present and valid
		if data['e_address'] == '':
			errors.append("Email may not be blank")
		if not EMAIL_REGEX.match(data['e_address']):
			errors.append("Please enter a valid email address.")
		#validate email uniqueness
		try:
			User.object.get(email=data['e_address'])
			print('dupe')
			errors.append("Email is already registered")
		except:
			pass
		# check password validations (>= 8 characters)
		# pw and confirm match
		if len(data['pass_word']) < 8:
			errors.append("Password must be at least eight characters long.")
		if data['pass_word'] != data['confirm_pass_word']:
			errors.append("Password does not match Confirm Password.")

		#and that we don't want to create any users yet...
		if len(errors) == 0:
			#no errors
			print('no errors')
			data['pass_word'] = bcrypt.hashpw(data['pass_word'].encode('utf-8'), bcrypt.gensalt())
			new_user = User.objects.create(first_name=data['fnom'], last_name=data['lnom'], email=data['e_address'], password=data['pass_word'])
			return {
				'new': new_user,
				'error_list': None
			}
		else:
			#yes errors
			print(errors)
			return {
				'new': None,
				'error_list': errors
			}
	def log(self, log_data):
		errors = []
		print log_data
		#check if user's account exists
		# """
		# log_data {
		# 	'e_mail': request.POST['email'],
		# 	'p_word': request.POST['password']
		# }
		# """
		try:
			found_user = User.objects.get(email=log_data['e_mail'])
			if bcrypt.hashpw(log_data['p_word'].encode('utf-8'), found_user.password.encode('utf-8')) != found_user.password.encode('utf-8'):
				errors.append("Incorrect password.")
		except:
			#email does not exist in the database
			errors.append("Email address not registered.")
		if len(errors) == 0:
			#no errors
			return {
				'logged_user': found_user,
				'list_errors': None
			}
		else:
			#found errors
			return {
				'logged_user': None,
				'list_errors': errors
			}

class User(models.Model):
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	password = models.CharField(max_length=255)
	objects = UserManager()

class Secret(models.Model):
	content = models.CharField(max_length=255)
	user = models.ForeignKey(User, related_name='secrets_created')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class Like(models.Model):
	user = models.ForeignKey(User, related_name='user_likes')
	secret = models.ForeignKey(Secret, related_name='secret_likes')
