# DRF gears ⚙ ⚙ ⚙

Some gears collection for getting life a little bit better.

## Installation

```
pip install drf-gears
```

## How to use

### ConditionalQuerysetMixin 

It gives you an ability to have multiple `get_queryset` methods for every needs.

#### Querysets mapping

`querysets` - is a dictionary of named querysets. You can provide different querysets for any action.

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from gears import ConditionalQuerysetMixin

from .models import MyModel


class MyModelViewSet(
    ConditionalQuerysetMixin,
    viewsets.ModelViewSet,
):
    querysets = {
        'list': MyModel.objects.all(),
        'custom': MyModel.objects.filter(),
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
from gears import ConditionalQuerysetMixin

from .models import MyModel

class MyModelViewSet(
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

E.g: `get_list_queryset`, `get_update_queryset`, `get_custom_action_queryset`.

```python
from rest_framework import viewsets
from gears import ConditionalQuerysetMixin

from .models import MyModel

class MyModelViewSet(
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

### PermissionsMixin

This part of specification is in progress.

### Renderers

There are a pair of things, which makes a charm when you work with API responses. 

Imagine, every API response has an expected structure. I mean every response!

For example, take a look at this paginated objects list API response:

```python
{
  "success": true,
  "status_code": 200,
  "pagination": {
    "count": 2,
    "next": null,
    "previous": null
  },
  "errors": [],
  "data": [
    {
      "id": "c65e9bf7-1724-4593-bf57-394cea491887",
      "phone_number": "10001001001"
    },
    {
      "id": "d7c9342d-0bd8-44e7-8e3c-44a18ecbfb8f",
      "phone_number": "10001001002"
    }
  ]
}
```

... and this validation error response.

```python
{
  "success": false,
  "status_code": 400,
  "pagination": null,
  "errors": [
    [
      {
        "code": "value_required",
        "location": "phone_number",
        "description": "This field is required.",
        "detail": null
      }
    ],
    [
      {
        "code": "value_required",
        "location": "password",
        "description": "This field is required.",
        "detail": null
      }
    ]
  ],
  "data": null
}
```

... and this authorization error too.

```python
{
  "success": false,
  "status_code": 403,
  "pagination": null,
  "errors": [
    {
      "code": "not_authenticated",
      "location": null,
      "description": "Authentication credentials were not provided.",
      "detail": null
    }
  ],
  "data": null
}
```

#### API renderer

All of these and any possible response will have the same structure: 
boolean `success`, integer `status_code`, `pagination` object, a list of `errors` objects and the requested `data` of course.

You should just use a single gear for it:

```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_RENDERER_CLASSES': (
        'gears.ApiRenderer',  # <-- that's it
    ),
    ...
}
```

#### Exception handler

Also, you could use the exception handler, if you want to see the same structure errors: 

```python
REST_FRAMEWORK = {
    ...
    'EXCEPTION_HANDLER': 'gears.exception_handler',  # <-- that's it
    ...
}
```

#### Error codes mapping

You have an ability to remap the standard error codes if you want. 
Yeah, sometimes the standard ones are not verbose enough. 
But you could handle this codes and remap them on your taste.
Just add the following settings variable and describe the errors' behaviour.
FYI, you're able to set not only the codes, but `description`, `details` and `location` are available as well.

```python
# setting.py

from gears import Error

RESPONSE_ERROR_MAPPING = {
    'required': Error(code='value_required'),
    ...
}
```
