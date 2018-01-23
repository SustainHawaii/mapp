from django.contrib.auth.models import BaseUserManager
import mongoengine as mongo
from mongoengine.django.mongo_auth.models import get_user_document
from maps.locations.models import Location, LocationType
from datetime import datetime
from maps.org.models import Organization
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.contrib.auth.hashers import (check_password, make_password, is_password_usable)

from maps.locations.json_views import verify_address
from maps.custom_form.serializers import FormSchemaIdSerializer
from mongoengine.queryset import QuerySet


class CustomUserQuerySet(QuerySet):

    def with_id(self, object_id):
        queryset = self.clone()
        # if not queryset._query_obj.empty:
        #     msg = "Cannot use a filter whilst using `with_id`"
        #     raise InvalidQueryError(msg)
        return queryset.filter(pk=object_id).first()


class UserTypes(mongo.Document):
    name = mongo.StringField(required=True, default='', unique=True)
    is_systemuser = mongo.BooleanField(default=False)
    is_superuser = mongo.BooleanField(default=False)
    permissions = mongo.DynamicField(required=True)
    allow_register = mongo.BooleanField(required=True)
    need_authorization = mongo.BooleanField(required=True)
    custom_field_form = mongo.ReferenceField("FormSchema", required=False)
    created = mongo.StringField(required=True, default=str(datetime.now()))
    updated = mongo.StringField(required=True, default=str(datetime.now()))

    @property
    def user_count(self):
        try:
            return User.objects.filter(user_types=self.id).count()
        except mongo.ValidationError:
            return 0

    @property
    def location_count(self):
        # TODO: how is the locations link with user or user type?
        return 0

    @property
    def group(self):
        return "User Types"

    @property
    def desc(self):
        return "User Type: %s -- Num Users: %d" % (self.name, self.user_count,)


    def has_permission(self, permission_type, action):
        perm = self.permissions.get(permission_type.lower())
        if perm:
            return bool(perm.get(action))
    
# IMPORTANT: make sure this is appear before the bridge class below!!!
# e.g. class MappUser
class User(mongo.Document):
    meta = {'queryset_class': CustomUserQuerySet,
            'allow_inheritance': True}

    full_name = mongo.StringField(verbose_name=_('full name'), max_length=30)
    email = mongo.EmailField(verbose_name=_('email address'), required=True, unique=True)
    password = mongo.StringField(max_length=128, verbose_name=_('password'))
    last_login = mongo.DateTimeField(verbose_name=_('last login'), default=timezone.now)
    is_staff = mongo.BooleanField(default=False)
    is_active = mongo.BooleanField(default=True)
    is_superuser = mongo.BooleanField(default=False)
    site_id = mongo.IntField(required=True, default=settings.SITE_ID)
    current_role = mongo.StringField(required=False)

    image = mongo.StringField(required=False)
    user_types = mongo.ListField(mongo.ReferenceField(UserTypes), required=True, verbose_name=_('User Types'))
    primary_user_type = mongo.ReferenceField(UserTypes, required=False, verbose_name=_('Primary User Type'))
    organization = mongo.ReferenceField(Organization, required=False, verbose_name=_('Organization'))
    custom_field_form = mongo.ReferenceField("FormSchema", required=False)
    activation_key = mongo.StringField(required=False)
    key_expires = mongo.DateTimeField(required=False)

    ban = mongo.BooleanField(default=False)
    ban_reason = mongo.StringField(max_length=255, required=False)

    address = mongo.StringField(max_length=255, required=False)
    city = mongo.StringField(max_length=255, required=False)
    state = mongo.StringField(max_length=255, required=False)
    zip = mongo.StringField(max_length=50, required=False)
    phone = mongo.StringField(max_length=20, required=False)
    description = mongo.StringField(required=False)
    point = mongo.PointField(required=False)

    #used for dashboard resource reference
    dashboard_resource_id = mongo.StringField(max_length=24, required=False)
    # TODO disabled for now, either needs to become a custom form, or hard coded like the address above
    # billing_phone = mongo.StringField(max_length=20, required=False, verbose_name=_('Billing Phone'))
    # shipping_phone = mongo.StringField(max_length=20, required=False, verbose_name=_('Shipping Phone'))

    # same_address = mongo.BooleanField(default=False, verbose_name=_('Is shipping adddress same as billing address'))
    # address_verified = mongo.BooleanField(default=False, verbose_name=_('Address verified by TaxCloud'))

    created = mongo.StringField(required=True, default=str(datetime.now()))
    updated = mongo.StringField(required=True, default=str(datetime.now()))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    @mongo.queryset.queryset_manager
    def objects(doc_cls, queryset):
        # This may actually also be done by defining a default ordering for
        # the document, but this illustrates the use of manager methods
        return queryset.filter(site_id=settings.SITE_ID)

    @mongo.queryset.queryset_manager
    def all(doc_cls, queryset):
        # This may actually also be done by defining a default ordering for
        # the document, but this illustrates the use of manager methods
        return queryset.all()

    def save(self, *args, **kwargs):
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.address and self.zip and self.city and self.state:
            address = (self.address + ", " + self.zip, self.city, self.state)
            geocoded_addr = verify_address(address)
            if geocoded_addr != 'Error':
                self.point = geocoded_addr

        super(User, self).save(*args, **kwargs)

        if not self.primary_user_type:
            self.set_primary_user_type()

    def set_current_role(self, role):
        self.current_role = role
        self.save()

    def set_primary_user_type(self, typ=None):
        admin = UserTypes.objects.get(name='Admin')
        if typ:
            typ = UserTypes.objects.get(name=typ)
        elif admin in self.user_types:
            typ = admin
        else:
            typ = self.user_types[0]
        self.primary_user_type = typ
        if self.site_id == 1:
            self.current_role = 'maps-admin'
        else:
            self.current_role = typ.name
        self.save()

    # def is_provider(self):
    #     return len(self.user_types.filter(type='provider')) > 0

    def get_username(self):
        "Return the identifying username for this User"
        return getattr(self, self.USERNAME_FIELD)

    def __unicode__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        return is_password_usable(self.password)

    def get_session_auth_hash(self):
        """
        Returns an HMAC of the password field.
        """
        key_salt = "maps.users.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def location_count(self):
        try:
            return Location.objects(created_by=str(self.id)).count()
        except mongo.ValidationError:
            return 0

    @property
    def image_url(self):
        url = None
        if self.image:
            url = settings.MEDIA_URL + self.image
        return url

    def custom_form(self):
        output = []
        try:
            if self.custom_field_form:
                serializer = FormSchemaIdSerializer(self.custom_field_form)
                output.append(serializer.data)
        except:
            pass
        return output

    def has_permission(self,obj_name, action):
        for ut in self.user_types:
            if ut.has_permission(obj_name, action):
                return True
                    
        return False

    def has_edit_other_permission(self, obj_name):
        return self.has_permission(obj_name, '4')

    def has_delete_other_permission(self, obj_name):
        return self.has_permission(obj_name, '5')

    def has_edit_own_permission(self, obj_name):
        return self.has_permission(obj_name, '1')

    def has_delete_own_permission(self, obj_name):
        return self.has_permission(obj_name, '2')

    def can_delete(self, obj, perm_type=None):
        if not perm_type:
            perm_type = obj.permission_type

        if obj.created_by == self.id:
            if self.has_delete_own_permission(perm_type):
                return True
        else:
            if self.has_delete_other_permission(perm_type):
                return True
        return False

    def can_edit(self, obj, perm_type=None):
        if not perm_type:
            perm_type = obj.permission_type

        if obj.created_by == self.id:
            if self.has_edit_own_permission(perm_type):
                return True
        else:
            if self.has_edit_other_permission(perm_type):
                return True
        return False


    @property
    def permission_type(self):
        return "users"

class UserManager(BaseUserManager):
    def _create_user(self, full_name, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given full_name, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(full_name=full_name, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, full_name, email=None, password=None, **extra_fields):
        return self._create_user(full_name, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, full_name, email, password, **extra_fields):
        extra_fields['user_types'] = [UserTypes.objects.get(name='Administrator')]
        return self._create_user(full_name, email, password, True, True,
                                 **extra_fields)


class MappUserManager(UserManager):
    def contribute_to_class(self, model, name):
        super(MappUserManager, self).contribute_to_class(model, name)
        self.dj_model = self.model
        self.model = get_user_document()

        self.dj_model.USERNAME_FIELD = self.model.USERNAME_FIELD
        self.dj_model.REQUIRED_FIELDS = self.model.REQUIRED_FIELDS

        """
        DO NOT create the fields using contribute_to_class function!
        """

    def get(self, *args, **kwargs):
        try:
            return self.get_queryset().get(*args, **kwargs)
        except self.model.DoesNotExist:
            # ModelBackend expects this exception
            raise self.dj_model.DoesNotExist

    @property
    def db(self):
        raise NotImplementedError

    def get_empty_query_set(self):
        return self.model.objects.none()

    def get_queryset(self):
        return self.model.objects


class MappUser(models.Model):
    """
    REMEMBER to create those required fields here! This is REQUIRED by creating
    user from command line!
    """
    email = models.EmailField(_('email address'), blank=True, unique=True)
    full_name = models.CharField(_('full name'), max_length=30, blank=True)

    objects = MappUserManager()

    class Meta:
        app_label = 'users'
