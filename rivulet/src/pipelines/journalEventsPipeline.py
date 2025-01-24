from knowledge.config_util import ConfigUtil
from datasources.journalEventsSource import JournalEventsSource
from framework.pipeline import Pipeline
from stages.journalEventsQuestions import JournalEventQuestions
from stages.journalEventEmbedding import JournalEventEmbedding
from stages.journalEventsStage import JournalEventsQAstage
from stages.journalEventSummary import JournalEventSummary

class JournalEventsPipeline:
    def __init__(self):
        self.configuration = ConfigUtil.get_knowledge_config()
        self.pipeline = Pipeline(data_source=JournalEventsSource())
        self.pipeline.add_stage(JournalEventsQAstage(self.configuration[0]))
        self.pipeline.add_stage(JournalEventSummary())
        self.pipeline.add_stage(JournalEventQuestions())
        self.pipeline.add_stage(JournalEventEmbedding())

    def run(self):
        return self.pipeline.run({"query": self.configuration[0]['query']})