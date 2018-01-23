import unittest

from maps.categories.models import Categories
from maps.locations.models import Location
from maps.data_import.models import DataImport
from datetime import datetime 


class TestCategory(unittest.TestCase):

   def setUp(self):
       for cat in Categories.objects.filter(name="test cat"):
           cat.delete()

       self.loc = Location(name="test_loc")
       self.loc.save()

   def tearDown(self):
        self.loc.delete()

   def test_cats_number_using(self):
       cat = Categories(name="test cat", tagged=[self.loc])
       cat.save()
       self.assertEqual(1, cat.number_using)
       cat.delete()

   def test_cats_tagged_holds_anything(self):
       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       cat = Categories(name="test cat", tagged=[self.loc, di])
       cat.save()
       self.assertEqual(2, cat.number_using)
       cat.delete()
       di.delete()


   def test_cats_for_obj_id(self):
       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       cat = Categories(name="test cat", tagged=[self.loc, di])
       cat.save()
       found_cats = Categories.for_object_id(str(di.id), "DataImport")
       self.assertEqual(1, len(found_cats))

       cat.delete()
       di.delete()

   def test_cats_get_all_tagged(self):

       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       cat = Categories(name="test cat1", tagged=[self.loc, di])
       cat.save()

       tagged = Categories.objects_with("test cat1")
       self.assertEqual(tagged, [self.loc, di])
    
       cat.delete()
       di.delete()

   def test_for_object(self):
       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       cat = Categories(name="test cat", tagged=[self.loc, di])
       cat.save()
       self.assertEqual(cat.name, Categories.for_object(di)[0].name)
       self.assertEqual(1, len(Categories.for_object(di)))
       self.assertEqual(cat.name, Categories.for_object(self.loc)[0].name)
       self.assertEqual(1, len(Categories.for_object(self.loc)))
       cat.delete()
       di.delete()

   def test_add_object(self):

       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       cat = Categories(name="test cat", tagged=[di])
       cat.save()

       tagged = Categories.objects_with("test cat")
       self.assertEqual(tagged, [di])
       
       cat.add_object(self.loc)

       tagged = Categories.objects_with("test cat")
       self.assertEqual(tagged, [di, self.loc])

       cat.delete()
       di.delete()


   def test_remove_obj(self):
       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       cat = Categories(name="test cat", tagged=[self.loc, di])
       cat.save()
       cat2 = Categories(name="garfield", tagged=[self.loc])
       cat2.save()
       
       self.assertEqual(2, len(Categories.for_object(self.loc)))

       Categories.remove_obj(self.loc)

       self.assertEqual(0, len(Categories.for_object(self.loc)))

       di.delete()
       cat.delete()
       cat2.delete()

       
       









   def test_cats_get_all_tagged_handles_missing(self):
       tagged = Categories.objects_with("I'm not there")
       self.assertEqual(tagged, [])

       



