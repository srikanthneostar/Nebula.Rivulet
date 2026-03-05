from knowledge.config_util import ConfigUtil
from datasources.journalEventsSource import JournalEventsSource
from framework.pipeline import Pipeline
from stages.journalEventsQuestions import JournalEventQuestions

class JournalEventsPipeline:
    def __init__(self):
        self.configuration = ConfigUtil.get_knowledge_config(self)
        self.pipeline = Pipeline(data_source=JournalEventsSource())
        self.pipeline.add_stage(JournalEventQuestions())

    def run(self):
        return self.pipeline.run({"query": self.configuration[1]['query']})
