class SerializersMixin(object):
    """
    SerializersMixin ...
    """
    serializers = {}
    serializer_class = None
    default_name = 'default'
    _serializers = {
        default_name: serializer_class,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.serializer_class and not self.serializers.get(self.default_name):
            raise ValueError(
                "Need to specify either 'serializer_class' or "
                "'serializers default' class"
            )
        self._serializers.update(self.serializers)

    def get_serializer_class(self, serializer_name=None):
        return self.serializers.get(serializer_name) \
               or self.serializers.get(self.action) \
               or self.serializers.get(self.default_name) \
               or super().get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class(
            serializer_name=kwargs.pop('serializer_name', None)
        )
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
