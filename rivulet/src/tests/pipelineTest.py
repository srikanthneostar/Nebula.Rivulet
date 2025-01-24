from pipelines.journalEventsPipeline import JournalEventsPipeline

def main():
    pipeline = JournalEventsPipeline()
    pipeline.run()

if __name__ == "__main__":
    main()
