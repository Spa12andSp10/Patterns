from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Logics.convert_chain import convert_chain
from Src.Logics.walker import walker
from Src.Logics import convert_strategies as st


class convert_factory(abstract_convert_factory):

    def create(self) -> "convert_factory":
        """Создаёт фабрику с набором стандартных стратегий.

        Порядок регистрации = приоритет:
          1. примитивы (str/int/float, кроме bool);
          2. даты;
          3. ссылочные модели (abstract_model, с защитой от циклов);
          4. произвольные объекты с публичными property;
          5. списки/кортежи;
          6. словари;
        """
        chain = (
            convert_chain()
            .register(st.is_simple, st.handle_simple)
            .register(st.is_date, st.handle_date)
            .register(st.is_reference, st.handle_reference)
            .register(st.is_object_with_properties, st.handle_object_with_properties)
            .register(st.is_list, st.handle_list)
            .register(st.is_dict, st.handle_dict)
        )
        return walker(chain)



