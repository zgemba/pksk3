import os
import unittest

from app import create_app
from app.myutils import allowed_file, make_unique_filename, get_from_gdrive


class MyUtilstestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_allowed_file(self):
        self.assertFalse(allowed_file("test.xxx"))
        self.assertTrue(allowed_file("test.jpg"))

    def test_make_unique_filename(self):
        filename = os.path.join(self.app.config["UPLOAD_SAVE_FOLDER"], "testing.tst")
        file = open(filename, "w")
        file.close()
        new_filename = make_unique_filename(filename)
        self.assertTrue(new_filename != filename)
        os.remove(filename)

    def test_gdrive_getter(self):
        sheet = get_from_gdrive("1KnfSG-v6JwLDW0vFe9E_hgDi17PfsZTPk7LuiCL9ybU")
        if sheet:
            if type(sheet) is int:
                self.fail("Error acessing gdrive ".format(str(sheet)))

            vals = sheet.sheet1.get_all_values()
            self.assertEqual(vals[0], ['Datum', 'Ime in priimek', 'Opombe', 'Preveril'])
        else:
            self.fail("Error acessing gdrive ")
