from types import ModuleType

import pytest

from flamapy.core import cache
from flamapy.core.models import VariabilityModel
from flamapy.core.plugins import Plugin
from flamapy.core.transformations import CacheableModelToModel


class SourceModel(VariabilityModel):
    @staticmethod
    def get_extension() -> str:
        return 'src'

    def __init__(self, content='payload', hashed=True):
        self.content = content
        self.hashed = hashed

    def canonical_hash(self):
        return f'hash-{self.content}' if self.hashed else None


class TargetModel(VariabilityModel):
    @staticmethod
    def get_extension() -> str:
        return 'tgt'

    def __init__(self, content, loaded_from_cache=False):
        self.content = content
        self.loaded_from_cache = loaded_from_cache


class FakeCacheableTransformation(CacheableModelToModel):
    artifact_suffix = 'fake'
    transform_calls = 0

    @staticmethod
    def get_source_extension() -> str:
        return 'src'

    @staticmethod
    def get_destination_extension() -> str:
        return 'tgt'

    def __init__(self, source_model):
        self.source_model = source_model

    def transform(self):
        FakeCacheableTransformation.transform_calls += 1
        return TargetModel(self.source_model.content)

    def dump_artifact(self, model, path):
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(model.content)

    def load_artifact(self, path, source_model):
        with open(path, encoding='utf-8') as handle:
            return TargetModel(handle.read(), loaded_from_cache=True)


@pytest.fixture(name='plugin')
def _plugin():
    module = ModuleType('flamapy.metamodels.fake_metamodel')
    plugin = Plugin(module=module)
    plugin.append_transformations(FakeCacheableTransformation)
    FakeCacheableTransformation.transform_calls = 0
    return plugin


@pytest.fixture(name='cache_env')
def _cache_env(tmp_path, monkeypatch):
    monkeypatch.setenv('FLAMAPY_CACHE', '1')
    monkeypatch.setenv('FLAMAPY_CACHE_DIR', str(tmp_path / 'cache'))
    return tmp_path / 'cache'


def test_disabled_by_default_writes_nothing(plugin, tmp_path, monkeypatch):
    monkeypatch.delenv('FLAMAPY_CACHE', raising=False)
    monkeypatch.setenv('FLAMAPY_CACHE_DIR', str(tmp_path / 'cache'))
    result = plugin.use_transformation_m2m(SourceModel(), 'tgt')
    assert not result.loaded_from_cache
    assert not (tmp_path / 'cache').exists()


def test_round_trip_hits_cache_on_second_call(plugin, cache_env):
    first = plugin.use_transformation_m2m(SourceModel(), 'tgt')
    assert not first.loaded_from_cache
    assert FakeCacheableTransformation.transform_calls == 1

    second = plugin.use_transformation_m2m(SourceModel(), 'tgt')
    assert second.loaded_from_cache
    assert second.content == first.content
    assert getattr(second, '_flamapy_cache_hit', False)
    assert FakeCacheableTransformation.transform_calls == 1  # no recomputation


def test_different_models_do_not_collide(plugin, cache_env):
    plugin.use_transformation_m2m(SourceModel('a'), 'tgt')
    other = plugin.use_transformation_m2m(SourceModel('b'), 'tgt')
    assert not other.loaded_from_cache
    assert other.content == 'b'


def test_hashless_models_bypass_the_cache(plugin, cache_env):
    plugin.use_transformation_m2m(SourceModel(hashed=False), 'tgt')
    result = plugin.use_transformation_m2m(SourceModel(hashed=False), 'tgt')
    assert not result.loaded_from_cache
    assert FakeCacheableTransformation.transform_calls == 2


def test_corrupt_artifact_recomputes(plugin, cache_env):
    plugin.use_transformation_m2m(SourceModel(), 'tgt')
    for artifact in cache_env.iterdir():
        artifact.unlink()
        artifact.mkdir()  # unreadable as a file -> load_artifact raises
    result = plugin.use_transformation_m2m(SourceModel(), 'tgt')
    assert not result.loaded_from_cache
    assert FakeCacheableTransformation.transform_calls == 2


def test_available_for_planner_hook(plugin, cache_env):
    source = SourceModel()
    assert not cache.available_for(source.canonical_hash(), 'tgt')
    plugin.use_transformation_m2m(source, 'tgt')
    assert cache.available_for(source.canonical_hash(), 'tgt')
    assert not cache.available_for(source.canonical_hash(), 'other')


def test_prune_drops_least_recently_used(cache_env, monkeypatch):
    cache_env.mkdir(parents=True)
    old = cache_env / 'old.fake'
    new = cache_env / 'new.fake'
    old.write_bytes(b'x' * 600_000)
    new.write_bytes(b'x' * 600_000)
    import os
    os.utime(old, (1, 1))
    monkeypatch.setenv('FLAMAPY_CACHE_MAX_MB', '1')
    cache.prune()
    assert not old.exists() and new.exists()


def test_info_and_clear(plugin, cache_env):
    plugin.use_transformation_m2m(SourceModel(), 'tgt')
    stats = cache.info()
    assert stats['enabled'] and stats['artifacts'] == 1
    assert cache.clear() == 1
    assert cache.info()['artifacts'] == 0
