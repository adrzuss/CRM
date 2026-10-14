"""
Tests para la migracion alembic que agrega impresion_directa a puntos_venta.

Estrategia (mock house style, sin MySQL real):
  - Carga el modulo de la revision con importlib (migrations/versions no es paquete).
  - Verifica la cadena de revisiones (un solo head, down_revision = c2d3df6d5f32).
  - Stub de op/inspect: comprueba que upgrade()/downgrade() son guardados por
    existencia (no-op seguro) y que la columna se crea con nullable=False
    y server_default.

La roundtrip real de upgrade/downgrade sobre MySQL queda como checklist
manual (AC-8); conftest.py no tiene harness de migraciones.
"""

import importlib.util
import re
from pathlib import Path

VERSIONS_DIR = Path(__file__).resolve().parents[1] / 'migrations' / 'versions'
ARCHIVO_REVISION = VERSIONS_DIR / '7e4b92c1d5a8_add_impresion_directa_puntos_venta.py'


def _cargar_revision():
    """Carga el modulo de la revision (los archivos de versions/ no son un paquete)."""
    spec = importlib.util.spec_from_file_location('rev_impresion_directa', ARCHIVO_REVISION)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _cadena_revisiones():
    """Parsea revision/down_revision de todos los .py de migrations/versions/."""
    parejas = []
    patron = re.compile(r"^(revision|down_revision)\s*=\s*['\"]([^'\"]+)['\"]", re.MULTILINE)
    for archivo in VERSIONS_DIR.glob('*.py'):
        datos = dict(patron.findall(archivo.read_text(encoding='utf-8')))
        if 'revision' in datos:
            parejas.append((datos['revision'], datos.get('down_revision')))
    return parejas


class _InspectorStub:
    """Simula sqlalchemy.inspect() con una lista fija de columnas."""

    def __init__(self, columnas):
        self._columnas = columnas

    def get_columns(self, tabla):
        return [{'name': c} for c in self._columnas]


class _OpStub:
    """Simula op de Alembic registrando las operaciones DDL emitidas."""

    def __init__(self):
        self.added = []
        self.dropped = []

    def get_bind(self):
        return object()

    def add_column(self, tabla, columna):
        self.added.append((tabla, columna))

    def drop_column(self, tabla, nombre):
        self.dropped.append((tabla, nombre))


def test_cadena_revisiones_un_solo_head():
    """La revision se encadena sobre c2d3df6d5f32 y queda como unico head."""
    modulo = _cargar_revision()

    assert modulo.down_revision == 'c2d3df6d5f32'

    parejas = _cadena_revisiones()
    hijos = {par for _, par in parejas if par}
    heads = [rev for rev, _ in parejas if rev not in hijos]

    assert heads == [modulo.revision]


def test_upgrade_agrega_columna_si_no_existe(monkeypatch):
    """Sin la columna: emite add_column con nullable=False y server_default."""
    modulo = _cargar_revision()
    op_stub = _OpStub()
    monkeypatch.setattr(modulo, 'op', op_stub)
    monkeypatch.setattr(modulo, 'inspect',
                        lambda conn: _InspectorStub(['id', 'punto_vta', 'pos_printer']))

    modulo.upgrade()

    assert len(op_stub.added) == 1
    tabla, columna = op_stub.added[0]
    assert tabla == 'puntos_venta'
    assert columna.name == 'impresion_directa'
    assert columna.nullable is False
    assert columna.server_default is not None


def test_upgrade_es_no_op_si_la_columna_ya_existe(monkeypatch):
    """Con la columna presente: re-ejecutar la revision no emite DDL."""
    modulo = _cargar_revision()
    op_stub = _OpStub()
    monkeypatch.setattr(modulo, 'op', op_stub)
    monkeypatch.setattr(modulo, 'inspect',
                        lambda conn: _InspectorStub(['id', 'impresion_directa']))

    modulo.upgrade()

    assert op_stub.added == []


def test_downgrade_guardado_por_existencia(monkeypatch):
    """downgrade() es simetrico: borra si existe, no-op si no."""
    modulo = _cargar_revision()
    op_stub = _OpStub()
    monkeypatch.setattr(modulo, 'op', op_stub)
    monkeypatch.setattr(modulo, 'inspect',
                        lambda conn: _InspectorStub(['id', 'impresion_directa']))

    modulo.downgrade()

    assert op_stub.dropped == [('puntos_venta', 'impresion_directa')]

    op_vacio = _OpStub()
    monkeypatch.setattr(modulo, 'op', op_vacio)
    monkeypatch.setattr(modulo, 'inspect', lambda conn: _InspectorStub(['id']))

    modulo.downgrade()

    assert op_vacio.dropped == []
