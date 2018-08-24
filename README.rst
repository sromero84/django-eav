django-eav
==========


Introduction
------------


**This is a fork of https://github.com/mvpdev/django-eav to adapt different things**:

- Make it Python 3 compatible
- Make it Django 2.0 compatible
- Remove dependency on Django Site framework
- Allow a custom Entity class and custom EntityManager class
- Allow an `Attribute` to be related to more than one `ContentType`
- Add `Decimal` attribute type (using django `DecimalValidator`)

The `EavConfig` now includes two new attributes `entity_class` and `entity_manager`, that default to `Entity` and `EntityManager` respectively.

What is this useful for? Let's say you want to filter the attributes of a given instance based on values, tags or any relational information related to that specific instance. Then, you could specify your custom `Entity` class and override the `get_all_attributes()` method.

--------

django-eav provides an Entity-Attribute-Value storage model for django apps.

For a decent explanation of what an Entity-Attribute-Value storage model is,
check `Wikipedia
<http://en.wikipedia.org/wiki/Entity-attribute-value_model>`_.

.. note::
   This software was inspired / derived from the excellent `eav-django
   <http://pypi.python.org/pypi/eav-django/1.0.2>`_ written by Andrey
   Mikhaylenko.

   There are a few notable differences between this implementation and the
   eav-django implementation.

   * This one is called django-eav, whereas the other is called eav-django.
   * This app allows you to to 'attach' EAV attributes to any existing django
     model (even from third-party apps) without making any changes to the those
     models' code.
   * This app has slightly more robust (but still not perfect) filtering.


Installation
------------

From Github
~~~~~~~~~~~
You can install django-eav directly from github::

    pip install -e git+git://github.com/sromero84/django-eav.git#egg=django-eav

Run ``migrate``


Usage
-----

Edit settings.py
~~~~~~~~~~~~~~~~
Add ``eav`` to your ``INSTALLED_APPS`` in your project's ``settings.py`` file.

Register your model(s)
~~~~~~~~~~~~~~~~~~~~~~
Before you can attach eav attributes to your model, you must register your
model with eav::

    >>> import eav
    >>> eav.register(MyModel)

Generally you would do this in your ``models.py`` immediate after your model
declarations. Alternatively, you can use the registration decorator provided::

    from eav.decorators import register_eav
    @register_eav()
    class MyModel(models.Model):
        ...

Create some attributes
~~~~~~~~~~~~~~~~~~~~~~
::

    >>> from eav.models import Attribute
    >>> Attribute.objects.create(name='Weight', datatype=Attribute.TYPE_FLOAT)
    >>> Attribute.objects.create(name='Color', datatype=Attribute.TYPE_TEXT)


Assign eav values
~~~~~~~~~~~~~~~~~
::

    >>> m = MyModel()
    >>> m.eav.weight = 15.4
    >>> m.eav.color = 'blue'
    >>> m.save()
    >>> m = MyModel.objects.get(pk=m.pk)
    >>> m.eav.weight
    15.4
    >>> m.eav.color
    blue

    >>> p = MyModel.objects.create(eav__weight = 12, eav__color='red')

Filter on eav values
~~~~~~~~~~~~~~~~~~~~
::

    >>> MyModel.objects.filter(eav__weight=15.4)

    >>> MyModel.objects.exclude(name='bob', eav__weight=15.4, eav__color='red')


Documentation and Examples
--------------------------

`<http://mvpdev.github.com/django-eav>`_
