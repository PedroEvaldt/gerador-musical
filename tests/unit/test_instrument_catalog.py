"""
Testes unitários do InMemoryInstrumentCatalog.
"""

import pytest

from music_generator.gui.instrument_catalog import InMemoryInstrumentCatalog


@pytest.fixture()
def catalog() -> InMemoryInstrumentCatalog:
    return InMemoryInstrumentCatalog()


class TestNomes:
    def test_names_retorna_128_instrumentos(self, catalog: InMemoryInstrumentCatalog) -> None:
        assert len(catalog.names()) == 128

    def test_names_nao_tem_duplicados(self, catalog: InMemoryInstrumentCatalog) -> None:
        nomes = catalog.names()
        assert len(nomes) == len(set(nomes))


class TestDefaultName:
    def test_default_name_esta_entre_os_nomes_disponiveis(
        self, catalog: InMemoryInstrumentCatalog
    ) -> None:
        assert catalog.default_name() in catalog.names()

    def test_default_name_e_o_primeiro_da_lista(self, catalog: InMemoryInstrumentCatalog) -> None:
        assert catalog.default_name() == catalog.names()[0]


class TestMidiProgram:
    def test_piano_acustico_grand_e_programa_zero(
        self, catalog: InMemoryInstrumentCatalog
    ) -> None:
        assert catalog.midi_program("Piano Acústico (Grand)") == 0

    def test_violino_e_programa_quarenta(self, catalog: InMemoryInstrumentCatalog) -> None:
        assert catalog.midi_program("Violino") == 40

    def test_todos_os_programas_no_intervalo_midi_valido(
        self, catalog: InMemoryInstrumentCatalog
    ) -> None:
        for nome in catalog.names():
            programa = catalog.midi_program(nome)
            assert 0 <= programa <= 127, f"{nome} fora do intervalo MIDI: {programa}"

    def test_todos_os_programas_sao_unicos(self, catalog: InMemoryInstrumentCatalog) -> None:
        programas = [catalog.midi_program(nome) for nome in catalog.names()]
        assert len(programas) == len(set(programas))

    def test_instrumento_inexistente_levanta_value_error(
        self, catalog: InMemoryInstrumentCatalog
    ) -> None:
        with pytest.raises(ValueError):
            catalog.midi_program("Theremin Quântico")
