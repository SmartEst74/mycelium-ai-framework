"""Mycelium pipeline payload module
Defines PipelinePayload and helpers for SCOUT→KNOW→SPAWN payloads.
This is an internal dispatch format (not an HTTP API).
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import uuid, json, datetime

@dataclass
class ScoutPhase:
    model: str = 'stepfun/step-3.5-flash:free'
    timeout_s: int = 30
    urls: List[str] = field(default_factory=list)
    depth: int = 1
    outputs: List[str] = field(default_factory=lambda: ['content', 'tech', 'structure'])

@dataclass
class KnowPhase:
    model: str = 'kilocode/xiaomi/mimo-v2-pro:free'
    tags: List[str] = field(default_factory=lambda: ['#lesson', '#pain-point'])
    routes: Dict[str, bool] = field(default_factory=lambda: {'lcmsession': True, 'qmd': True})
    transformations: List[Dict[str, Any]] = field(default_factory=lambda: [{'type': 'extract_summary'}, {'type': 'tag_and_route'}])

@dataclass
class SpawnTask:
    role: str
    instruction: str
    model: Optional[str] = None

@dataclass
class SpawnPhase:
    model_override: Optional[str] = None
    tasks: List[SpawnTask] = field(default_factory=list)
    parallel: bool = False

@dataclass
class PipelinePayload:
    schema: str = '/schemas/mycelium/pipeline-1.json'
    id: str = field(default_factory=lambda: 'pipeline-' + uuid.uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + 'Z')
    pipeline: List[Any] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=lambda: {'initiator': 'mycelium', 'tags': ['#mission']})

    def add_scout(self, scout: ScoutPhase):
        self.pipeline.append({
            'phase': 'scout',
            'model': scout.model,
            'timeout_s': scout.timeout_s,
            'input': {'urls': scout.urls, 'depth': scout.depth},
            'outputs': scout.outputs,
        })

    def add_know(self, know: KnowPhase):
        self.pipeline.append({
            'phase': 'know',
            'model': know.model,
            'routes': know.routes,
            'tags': know.tags,
            'transformations': know.transformations,
        })

    def add_spawn(self, spawn: SpawnPhase):
        self.pipeline.append({
            'phase': 'spawn',
            'model_override': spawn.model_override,
            'tasks': [asdict(t) for t in spawn.tasks],
            'parallel': spawn.parallel,
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            '$schema': self.schema,
            'id': self.id,
            'created_at': self.created_at,
            'pipeline': self.pipeline,
            'meta': self.meta,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def validate(self) -> bool:
        if not self.pipeline:
            raise ValueError('pipeline must contain at least one phase')
        allowed_order = ['scout', 'know', 'spawn']
        phases = [p.get('phase') for p in self.pipeline]
        # Ensure each phase is in allowed list
        for p in phases:
            if p not in allowed_order:
                raise ValueError(f"unknown phase '{p}' in pipeline")
        indices = [allowed_order.index(p) for p in phases]
        if indices != sorted(indices):
            raise ValueError('pipeline phases must be in order: scout -> know -> spawn')
        return True

# Convenience constructor
def make_default_pipeline(urls: List[str], tasks: List[Dict[str, Any]]):
    scout = ScoutPhase(urls=urls)
    know = KnowPhase()
    spawn_tasks = [SpawnTask(**t) for t in tasks]
    spawn = SpawnPhase(tasks=spawn_tasks)
    pp = PipelinePayload()
    pp.add_scout(scout)
    pp.add_know(know)
    pp.add_spawn(spawn)
    return pp
