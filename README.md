# DRF gears ⚙ ⚙ ⚙

Some cogs collection for getting life a little better.

## Installation

```
pip install django-msgs
```

## How to use

### ConditionalQuerysetMixin 

It gives you an ability to have multiple `get_queryset` methods for every needs.

#### Querysets mapping

`querysets` - is a dictionary of named querysets. You can provide different querysets for any action.

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_cogs.mixins import ConditionalQuerysetMixin

class SomeViewSet(
    ConditionalQuerysetMixin,
    viewsets.ModelViewSet,
):
    querysets = {
        'list': Model.objects.all(),
        'custom': Model.objects.filter(),
    }

    @action(methods=['get'])
    def some_action(self, request, *args, **kwargs):
        qs = self.get_queryset(name='custom')
        ...
```

#### Named queryset method

Use named methods like `get_name_queryset`, where `name` is an any name.

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_cogs.mixins import ConditionalQuerysetMixin

class SomeViewSet(
    ConditionalQuerysetMixin,
    viewsets.ModelViewSet,
):
    def get_custom_queryset(self, qs):
        # do something
        return qs

    @action(methods=['get'])
    def some_action(self, request, *args, **kwargs):
        qs = self.get_queryset(name='custom')
        ...
```

#### ViewSet actions

If ConditionalQuerysetMixin can't find a mapped or named queryset, it will try to find a method with a ViewSet action instead of name.

E.g: `get_list_queryset`, `get_update_queryset`, get_custom_action_queryset.

```python
from rest_framework import viewsets
from rest_cogs.mixins import ConditionalQuerysetMixin

class SomeViewSet(
    ConditionalQuerysetMixin,
    viewsets.ModelViewSet,
):
    def get_list_queryset(self, qs):
        # do something
        return qs
    
    def get_retrieve_queryset(self, qs):
        # do something
        return qs
    
    def get_some_action_queryset(self, qs):
        # do something
        return qs
```

### SerializersMixin

Use this mixin if you need different serializers for any action. 
By default, will be used a `serializer_class` or a `default` item of `serializers` dictionary.

By the way, you can change the default key providing `default_name` attribute.

```python
from rest_framework import viewsets
from rest_cogs.mixins import SerializersMixin

class SomeViewSet(
    SerializersMixin,
    viewsets.ModelViewSet,
):
    serializers = {
        'default': DefaultModelSerializer,
        'list': AdditionalModelSerializer,
    }
```

Also, you can use a `get_serializer` method providing a specific name when you need to use a particular serializer.

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_cogs.mixins import SerializersMixin

class SomeViewSet(
    SerializersMixin,
    viewsets.ModelViewSet,
):
    serializers = {
        'default': DefaultModelSerializer,
        'some_action': SomeActionModelSerializer,
        'list': ListModelSerializer,
    }

    @action(methods=['get'])
    def some_action(self, request, *args, **kwargs):
        serializer = self.get_serializer()  # SomeActionModelSerializer
        serializer = self.get_serializer(serializer_name='list')  # ListModelSerializer
        ...
```
