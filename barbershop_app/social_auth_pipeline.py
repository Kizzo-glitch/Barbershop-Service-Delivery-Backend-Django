from .models import Customer, Barber


def create_user_by_type(backend, user, request, response, *args, **kwargs):
	request = backend.strategy.request_data()
	if backend.name == 'facebook':
		avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']



	if request['user_type'] == "barber" and not Barber.objects.filter(user_id=user.id):
		Barber.objects.create(user_id=user.id, avatar = avatar)
	elif request['user_type'] == "customer" and not Customer.objects.filter(user_id=user.id):
		Customer.objects.create(user_id=user.id, avatar = avatar)
