from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Logics.deserialize_chain import deserialize_chain
from Src.Logics.model_resolver import model_resolver
from Src.Logics import deserialize_strategies as st


class deserialize_factory(abstract_deserialize_factory):
    """Цепочка десериализации (зеркальный класс для сериализации)"""

    def __init__(self):
        self._resolver = model_resolver()

    @property
    def resolver(self) -> model_resolver:
        return self._resolver

    def create(self) -> deserialize_chain:
        return (
            deserialize_chain()
            .register(st.is_date_value,   st.handle_date)
            .register(st.is_value,        st.handle_value)
            .register(st.is_indexed_dict, st.handle_indexed_dict)
            .register(st.is_model_dict,   st.handle_model)
            .register(st.is_plain_dict,   st.handle_dict)
        )

    def deserialize(self, source):
        return self.create().deserialize(source, self._resolver, set())

    def clear(self) -> None:
        self._resolver.clear()