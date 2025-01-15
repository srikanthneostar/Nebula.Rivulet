from typing import List, Dict, Any
import logging
from .pipeline_stage import PipelineStage
from .data_source import DataSource

class Pipeline:
    def __init__(self, data_source: DataSource):
        self.data_source = data_source
        self.stages: List[PipelineStage] = []
        self.logger = logging.getLogger(__name__)

    def add_stage(self, stage: PipelineStage):
        self.stages.append(stage)

    def run(self, query: any) -> Any:
        data = self.data_source.get_data(query)
        self.logger.info(f"Retrieved {len(data)} records from Elasticsearch")

        for stage in self.stages:
            self.logger.info(f"Running stage: {stage.__class__.__name__}")
            data = stage.process(data)

        return data
