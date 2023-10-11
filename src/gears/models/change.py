from typing import List, Tuple

from django.db import models


class OnChangeModel(models.Model):
    """
    Handle fields edition logic by the custom methods.
    You have two options which could works together. The first one is a list of model
    fields, which will be processed by the main on_change method. By default, it does
    nothing, so take care to write your own on_change method.
    The second one is a multiple custom methods, a single for any field you want
    to handle up. Name these methods like `on_change_<field_name>`. BTW, you're able to
    rename this prefix by the `on_change_prefix`.
    Keep on mind, if you use the on_change_field method, it will be executed first, and
    the main on_change method will be executed last.
    You can manage the main on_change method from the on_change_field methods by
    returning the status value. It shows your desire the main on_change method working
    on this field or not.

    on_change_fields -- A list of field for processing by OnChangeModel. All of them
    will be processed by the on_change method.

    Create a method with name like 'on_change_<field_name>' for handling fields with
    separated method.

    on_change_prefix -- a prefix for methods naming.
    origin_prefix -- a prefix for attributes where serves the origin values.
    """

    # It would be nice to make a decorator @on_change(field1, field2...)

    on_change_fields = ()
    on_change_prefix = 'on_change_'
    origin_prefix = '__origin_'

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("\nINIT")
        for name in self.get_on_change_fields():
            print(name, self.get_origin_name(name), getattr(self, name, None))
            setattr(self, self.get_origin_name(name), getattr(self, name, None))

    def save(self, *args, **kwargs):
        self.process_changed_fields()
        print(self.name)
        super().save(*args, **kwargs)
        self.after_save()

    def execute_on_change_method(self, origin_name, origin_value, name, value) -> bool:
        """
        This method executes the custom model's on_change method.
        On_change methods could impact on the values will be set. So take care
        to return the status of its work.
        The status is a boolean indicator of the on_change method, where True means
        this field should be passed to the main on_change method, and False
        means it shouldn't.
        :param origin_name: the prefixed name of an attribute where the original value
        is stored
        :param origin_value: the original value of the field
        :param name: a name of the field
        :param value: new value of the field
        :return: status - must be processed by the main on_change method or must not.
        """
        method = self._get_method(name)
        if not method:
            return True  # must be processed by the main on_change method
        _status = method(origin_value, value)
        # This is a compatibility part. Previous lib version might return nothing.
        _status = True if _status is None else _status
        # set new value as original value preventing extra method execution
        setattr(self, origin_name, value)
        return _status

    def get_origin_name(self, name):
        return f'{self.origin_prefix}{name}'

    def get_origin_value(self, origin_name):
        return getattr(self, origin_name)

    def process_changed_fields(self):
        changed_fields = self.get_changed_fields()
        on_change_attrs = []
        for origin_name, origin_value, name, value in changed_fields:
            attrs = origin_name, origin_value, name, value
            status = self.execute_on_change_method(*attrs)
            if status is True:
                on_change_attrs.append(attrs)
        self.on_change(on_change_attrs)

    def after_save(self):
        """Customize it on your taste"""
        pass

    def on_change(self, fields: List[Tuple]):
        """
        This method allows to implement the logic based on the whole
        changed fields list. It works only with the field defined in the
        `on_change_fields` attribute. If you need to handel a single field only you
        should use the model's method named like `on_change_FIELD_NAME`.
        These method will be processed automatically, based on th `on_change_prefix`
        attribute.
        """
        for origin_name, origin_value, name, value in fields:
            pass  # handle logic here

    def get_on_change_fields(self):
        # Combine manually added fields with the defined through method fields
        fields = self.get_on_change_methods()
        fields.extend(self.on_change_fields)
        return fields

    def get_on_change_methods(self):
        def is_on_change_method(a):
            return a.startswith(self.on_change_prefix) and callable(getattr(self, a))
        l = len(self.on_change_prefix)
        return [attr[l:] for attr in dir(self) if is_on_change_method(attr)]

    def get_changed_fields(self) -> List[Tuple]:
        for name in self.get_on_change_fields():
            origin_name = self.get_origin_name(name)
            origin_value = self.get_origin_value(origin_name)
            value = getattr(self, name)
            if value != origin_value:
                yield origin_name, origin_value, name, value

    def _get_method(self, field_name: str):
        method_name = f'{self.on_change_prefix}{field_name}'
        try:
            return getattr(self, method_name)
        except AttributeError:
            # f'OnChangeModel has no method {method_name}'
            return
