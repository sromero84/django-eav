from django.contrib.auth.models import User
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

import eav

from ..models import Attribute, EnumGroup, EnumValue, Value
from ..registry import EavConfig
from .models import Encounter, Patient


class DataValidation(TestCase):

    def setUp(self):
        eav.register(Patient)

        Attribute.objects.create(name='Age', datatype=Attribute.TYPE_INT)
        Attribute.objects.create(name='DoB', datatype=Attribute.TYPE_DATE)
        Attribute.objects.create(name='Height', datatype=Attribute.TYPE_FLOAT)
        Attribute.objects.create(name='Money', datatype=Attribute.TYPE_DECIMAL)
        Attribute.objects.create(name='City', datatype=Attribute.TYPE_TEXT)
        Attribute.objects.create(name='Pregnant?', datatype=Attribute.TYPE_BOOLEAN)
        Attribute.objects.create(name='User', datatype=Attribute.TYPE_OBJECT)
        Attribute.objects.create(name='Address', datatype=Attribute.TYPE_POINT)
        Attribute.objects.create(name='Zone', datatype=Attribute.TYPE_MULTIPOLYGON)

    def tearDown(self):
        eav.unregister(Patient)

    def test_required_field(self):
        p = Patient(name='Bob')
        p.eav.age = 5
        p.save()

        Attribute.objects.create(name='Weight', datatype=Attribute.TYPE_INT, required=True)
        p.eav.age = 6
        self.assertRaises(ValidationError, p.save)
        p = Patient.objects.get(name='Bob')
        self.assertEqual(p.eav.age, 5)
        p.eav.weight = 23
        p.save()
        p = Patient.objects.get(name='Bob')
        self.assertEqual(p.eav.weight, 23)

    def test_create_required_field(self):
        Attribute.objects.create(name='Weight', datatype=Attribute.TYPE_INT, required=True)
        self.assertRaises(ValidationError,
                          Patient.objects.create,
                          name='Joe', eav__age=5)
        self.assertEqual(Patient.objects.count(), 0)
        self.assertEqual(Value.objects.count(), 0)

        p = Patient.objects.create(name='Joe', eav__weight=2, eav__age=5)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Value.objects.count(), 2)

    def test_validation_error_create(self):
        self.assertRaises(ValidationError,
                          Patient.objects.create,
                          name='Joe', eav__age='df')
        self.assertEqual(Patient.objects.count(), 0)
        self.assertEqual(Value.objects.count(), 0)

    def test_bad_slug(self):
        a = Attribute.objects.create(name='color', datatype=Attribute.TYPE_TEXT)
        a.slug = 'Color'
        self.assertRaises(ValidationError, a.save)
        a.slug = '1st'
        self.assertRaises(ValidationError, a.save)
        a.slug = '_st'
        self.assertRaises(ValidationError, a.save)

    def test_changing_datatypes(self):
        a = Attribute.objects.create(name='Color', datatype=Attribute.TYPE_INT)
        a.datatype = Attribute.TYPE_TEXT
        a.save()
        Patient.objects.create(name='Bob', eav__color='brown')
        a.datatype = Attribute.TYPE_INT
        self.assertRaises(ValidationError, a.save)

    def test_int_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.age = 'bad'
        self.assertRaises(ValidationError, p.save)
        p.eav.age = 15
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.age, 15)

    def test_date_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.dob = 'bad'
        self.assertRaises(ValidationError, p.save)
        p.eav.dob = 15
        self.assertRaises(ValidationError, p.save)
        now = timezone.now()
        now = timezone.datetime(year=now.year, month=now.month, day=now.day,
                                hour=now.hour, minute=now.minute, second=now.second)
        p.eav.dob = now
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.dob, now)
        today = timezone.today()
        p.eav.dob = today
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.dob.date(), today)

    def test_decimal_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.money = 'bad'
        self.assertRaises(ValidationError, p.save)
        p = Patient.objects.create(name='Joe')
        p.eav.money = '10.2030348884'
        self.assertRaises(ValidationError, p.save)
        p.eav.money = 15
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.money, Deimal(15))
        p.eav.money = '15.23'
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.money, Decimal('15.23'))
        p.eav.money= 20.55
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.money, Decimal(20.55))

    def test_float_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.height = 'bad'
        self.assertRaises(ValidationError, p.save)
        p.eav.height = 15
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.height, 15)
        p.eav.height='2.3'
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.height, 2.3)

    def test_text_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.city = 5
        self.assertRaises(ValidationError, p.save)
        p.eav.city = 'El Dorado'
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.city, 'El Dorado')

    def test_bool_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.pregnant = 5
        self.assertRaises(ValidationError, p.save)
        p.eav.pregnant = True
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.pregnant, True)

    def test_object_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.user = 5
        self.assertRaises(ValidationError, p.save)
        p.eav.user = object
        self.assertRaises(ValidationError, p.save)
        p.eav.user = User(username='joe')
        self.assertRaises(ValidationError, p.save)
        u = User.objects.create(username='joe')
        p.eav.user = u
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.user, u)

    def test_enum_validation(self):
        yes = EnumValue.objects.create(value='yes')
        no = EnumValue.objects.create(value='no')
        unkown = EnumValue.objects.create(value='unkown')
        green = EnumValue.objects.create(value='green')
        ynu = EnumGroup.objects.create(name='Yes / No / Unknown')
        ynu.enums.add(yes)
        ynu.enums.add(no)
        ynu.enums.add(unkown)
        Attribute.objects.create(name='Fever?', datatype=Attribute.TYPE_ENUM, enum_group=ynu)

        p = Patient.objects.create(name='Joe')
        p.eav.fever = 5
        self.assertRaises(ValidationError, p.save)
        p.eav.fever = object
        self.assertRaises(ValidationError, p.save)
        p.eav.fever = 'yes'
        self.assertRaises(ValidationError, p.save)
        p.eav.fever = green
        self.assertRaises(ValidationError, p.save)
        p.eav.fever = EnumValue(value='yes')
        self.assertRaises(ValidationError, p.save)
        p.eav.fever = no
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.fever, no)

    def test_enum_datatype_without_enum_group(self):
        a = Attribute(name='Age Bracket', datatype=Attribute.TYPE_ENUM)
        self.assertRaises(ValidationError, a.save)
        yes = EnumValue.objects.create(value='yes')
        no = EnumValue.objects.create(value='no')
        unkown = EnumValue.objects.create(value='unkown')
        ynu = EnumGroup.objects.create(name='Yes / No / Unknown')
        ynu.enums.add(yes)
        ynu.enums.add(no)
        ynu.enums.add(unkown)
        a = Attribute(name='Age Bracket', datatype=Attribute.TYPE_ENUM, enum_group=ynu)
        a.save()

    def test_enum_group_on_other_datatype(self):
        yes = EnumValue.objects.create(value='yes')
        no = EnumValue.objects.create(value='no')
        unkown = EnumValue.objects.create(value='unkown')
        ynu = EnumGroup.objects.create(name='Yes / No / Unknown')
        ynu.enums.add(yes)
        ynu.enums.add(no)
        ynu.enums.add(unkown)
        a = Attribute(name='color', datatype=Attribute.TYPE_TEXT, enum_group=ynu)
        self.assertRaises(ValidationError, a.save)

    def test_point_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.address = True
        self.assertRaises(ValidationError, p.save)
        point = Point(12.4604, 43.9420)
        p.eav.address = point
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.address, point)

    def test_multipolygon_validation(self):
        p = Patient.objects.create(name='Joe')
        p.eav.zone = True
        self.assertRaises(ValidationError, p.save)
        poly1 = Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0)))
        poly2 = Polygon(((50.0, 50.0), (50.0, 80.0), (80.0, 80.0), (80.0, 50.0), (50.0, 50.0)))
        multipoly = MultiPolygon((poly1, poly2))
        p.eav.zone = multipoly
        p.save()
        self.assertEqual(Patient.objects.get(pk=p.pk).eav.zone, multipoly)
