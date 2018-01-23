from maps.users.models import User, UserTypes
from django.test import TestCase

class UserTypesTests(TestCase):

    def setUp(self):
        self.perms = {
            "category": {
                "1": True, 
                "0": True, 
                "3": True, 
                "2": True, 
                "5": True, 
                "4": True, 
                "7": False, 
                "6": False 
            }, 
            "users": {
                "1": True, 
                "0": True, 
                "3": True, 
                "2": True, 
                "5": True, 
                "4": True, 
                "7": False, 
                "6": False 
            }, 
        }
        self.userType = UserTypes(name="tester",
                                 permissions=self.perms,allow_register=True,
                                 need_authorization=True)
        self.userType.save()

        self.user = User(name="fred",user_types=[self.userType,],site_id=1,
                         email="test@test.com", password="123")
                         
    def tearDown(self):
        self.userType.delete()

    def test_permissions(self):
        self.assertTrue(self.userType.has_permission("users", "1"))
        self.assertTrue(self.userType.has_permission("users", "2"))
        self.assertTrue(self.userType.has_permission("users", "3"))
        self.assertTrue(self.userType.has_permission("users", "4"))
        self.assertTrue(self.userType.has_permission("users", "5"))
        self.assertTrue(self.userType.has_permission("users", "5"))
        self.assertFalse(self.userType.has_permission("users", "6"))
        self.assertFalse(self.userType.has_permission("users", "7"))
        self.assertFalse(self.userType.has_permission("category", "7"))


    def test_permissions_handles_incorrect_case(self):
        self.assertFalse(self.userType.has_permission("Category", "7"))


    def test_permission_from_user(self):
        self.assertTrue(self.user.has_edit_other_permission("users"))
        self.assertTrue(self.user.has_delete_other_permission("users"))
        self.assertTrue(self.user.has_edit_own_permission("users"))
        self.assertTrue(self.user.has_delete_own_permission("users"))
