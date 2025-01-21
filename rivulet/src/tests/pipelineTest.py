from pipelines.journalEventsPipeline import JournalEventsPipeline

def main():
    pipeline = JournalEventsPipeline()
    pipeline.Run()

if __name__ == "__main__":
    main()
