from django.template import RequestContext
from django.utils import timezone
from rest_framework import permissions
from rest_framework_mongoengine.generics import CreateAPIView
from mappweb.settings import PERMISSION
from django.conf import settings
from maps.org.models import Organization
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from maps.users.models import User, UserTypes
from mongoengine.queryset import DoesNotExist
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render_to_response, redirect, Http404
from rest_framework.response import Response
from maps.users.serializers import UserSerializer
from rest_framework import status
from .tasks import *
import json
from django.http import HttpResponse

role = 'maps-admin'
template_base_path = 'maps-admin/users/'


def init_data():
    return {
        'role': role,
    }


# @api_view(['GET'])
@login_required(login_url='/')
def users(request):
    data = init_data()
    data['user'] = User.objects.all()
    data['orgs'] = Organization.objects.all()

    return render_to_response(template_base_path + 'users.html', data, context_instance=RequestContext(request))


# @api_view(['GET'])
@login_required(login_url='/')
def user_add(request):
    data = init_data()
    return render_to_response(template_base_path + 'users-adduser.html', data, context_instance=RequestContext(request))


# @api_view(['GET'])
@login_required(login_url='/')
def user_update(request, user_id):
    data = init_data()
    data['object'] = User.objects.get(id=user_id)
    return render_to_response(template_base_path + 'users-adduser.html', data, context_instance=RequestContext(request))


@login_required(login_url='/')
def user_types(request):
    data = init_data()
    data['data'] = UserTypes.objects.all()
    return render_to_response(template_base_path + 'users-usertypes.html', data, context_instance=RequestContext(request))


# @api_view(['GET'])
@login_required(login_url='/')
def user_type_add(request):
    data = init_data()
    data['permissions'] = PERMISSION
    return render_to_response(template_base_path + 'users-addusertype.html', data, context_instance=RequestContext(request))


# @api_view(['GET'])
@login_required(login_url='/')
def user_type_update(request, user_type_id):
    data = init_data()
    data['permissions'] = PERMISSION
    data['data'] = UserTypes.objects.get(id=user_type_id)
    return render_to_response(template_base_path + 'users-addusertype.html', data, context_instance=RequestContext(request))


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request):
    try:
        user = User.objects.get(email=request.DATA['email'])
    except DoesNotExist:
        return Response(
        {
            'success': False,
            'message': "Incorrect email or password."
        }, status=status.HTTP_406_NOT_ACCEPTABLE)

    if user.check_password(request.DATA['password']) and user.is_active:
        user.backend = 'mongoengine.django.auth.MongoEngineBackend'
        auth_login(request, user)

        if request.user.is_authenticated():
            return Response(
            {
                'success': True,
                'message': 'Login successful.',
                "next": get_next_page(request, user)
            }, status=status.HTTP_200_OK)
    else:
        return Response(
        {
            'success': False,
            'message': "Incorrect email or password."
        }, status=status.HTTP_404_NOT_FOUND)


class SignUpView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def process_data(self, request):
        data = request.DATA
        response = None
        try:
            if 'user_types' in data:
                if len(data['user_types']) == 0:
                    data = None
                    response = Response({
                        'success': False,
                        'errors': {
                            'user_type': [u'Must select at least 1 type.']
                        }
                    })
                ut, data['user_types'] = data['user_types'], []
                for u in ut:
                    try:
                        data['user_types'].append(UserTypes.objects.get(id=u))
                    except UserTypes.DoesNotExist:
                        data = None
                        response = Response({
                            'success': False,
                            'errors': {
                                'user_type': [u'Invalid user type %s.' % u]}})

        except KeyError:
            data = request.DATA
        return {"data": data, "response": response}

    def post(self, request, *args, **kwargs):
        data = self.process_data(request)
        if data["response"]:
            return data["response"]

        try:
            serializer = self.get_serializer(
                data=data['data'], files=request.FILES)
            if serializer.is_valid():
                self.pre_save(serializer.object)
                self.object = serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED,
                                headers=headers)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print e
            return Response({'Error': e._message}, status=status.HTTP_400_BAD_REQUEST)

    def post_save(self, obj, created=False):
        if created:
            try:
                obj.set_password(self.request.DATA['password'])
                obj.save()

                # email validation
                site = self.request.META['HTTP_HOST']
                user_id = obj.id
                send_email_confirmation(site, user_id)
            except Exception as e:
                print e


def logout_view(request):
    auth_logout(request)
    return redirect('/')


def register_confirm(request, auth_key):
    try:
        user = User.objects.get(activation_key=auth_key)
    except DoesNotExist:
        raise Http404
    if user.key_expires < timezone.now():
        messages.error(request, 'Your activation key is expired.')
        return redirect('/')

    user.is_active = True
    user.save()
    messages.success(
        request, 'Your account has been activated. Please log in with your credentials.')
    return redirect('/')


def password_recover(request):
    try:
        site = request.META['HTTP_HOST']
        data = json.loads(request.body)
        if 'email' in data:
            email = data['email']

        user = User.objects.get(email=email)
        send_email_recovery(site, user)

        res = {
            'success': True,
            'message': 'Successful.',
        }
        res = json.dumps(res)
        return HttpResponse(res, content_type="application/json")
    except Exception as e:
        res = {'success': False, 'message': str(e)}
        res = json.dumps(res)
        return HttpResponse(res, content_type="application/json")


def password_reset(request, auth_key):
    try:
        user = User.objects.get(activation_key=auth_key)
    except DoesNotExist:
        raise Http404
    if user.key_expires < timezone.now():
        messages.error(request, 'Your activation key is expired.')
        return redirect('/')

    if request.method == 'POST':
        pwd = request.POST.get('password', None)
        repeat = request.POST.get('repeat-password', None)
        if pwd != repeat:
            messages.error(request, "Password doesn\'t match.")
        else:
            user.set_password(pwd)
            user.save()
            messages.success(request, 'Password successfully reset.')
    return render_to_response('homepage/password-reset.html', context_instance=RequestContext(request))


def get_next_page(request, user):
    if settings.SITE_ID == 2:
        return '/' + (user.user_types[0].name).lower() + '/dashboard'
    try:
        if len(request.META['HTTP_REFERER'].split('?next=')) > 0:
            return request.META['HTTP_REFERER'].split('?next=')[1]
    except Exception:
        return '/'
