from configuration.config_util import ConfigUtil
from datasources.journalEventsSource import JournalEventsSource
from framework.pipeline import Pipeline
from stages.journalEventsStage import JournalEventsQAstage
from stages.journalEventSummary import JournalEventSummary
class JournalEventsPipeline:
    def __init__(self):
        self.configuration = ConfigUtil().get_knowledge_config()[0]
        self.pipeline = Pipeline(data_source=JournalEventsSource())
        self.pipeline.add_stage(JournalEventsQAstage(self.configuration))
        self.pipeline.add_stage(JournalEventSummary())
    def Run():
        pass