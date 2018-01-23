import unittest
from mock import MagicMock

# from django.contrib.messages.middleware import MessageMiddleware

# from user.models import User as ShopUser
from maps.users.models import User as MapUser, UserTypes

user = MagicMock(spec=MapUser)
user_type = MagicMock(spec=UserTypes)
user_type.name = 'admin'

user.check_password = MagicMock(return_value=True)
user.user_type = [user_type]

@unittest.skip("")
class MapsFixtures(unittest.TestCase):

    def setUp(self):
        from maps.fixtures.users.script import create_fixtures
        create_fixtures()

    def tearDown(self):
        pass

    def test_maps_using_test_mongodb(self):
        import mongoengine.connection as mongo
        mongo.connect('default')
        db_name = mongo.get_db('test')
        self.assertEqual('test_Maps', db_name.name)
        self.assertEqual(MapUser._get_db().name, 'test')

    def test_djangoshop_fixtures_add_6_users_to_mongo(self):
        self.assertEqual(MapUser.all().count(), 7)

@unittest.skip("")
class UserModel(unittest.TestCase):

    def setUp(self):
        from maps.fixtures.users.script import create_fixtures
        create_fixtures()

    def tearDown(self):
        pass

    def test_user_model_custom_queryset_returns_site_id_1_only(self):
        users = MapUser.objects
        for user in users:
            self.assertEqual(user.site_id, 1)





