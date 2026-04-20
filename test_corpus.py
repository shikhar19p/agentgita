from src.core.corpus_validator import CorpusLoader
import json

loader = CorpusLoader('data/corpus.json')
loader.load()

print('\nCorpus Stats:')
print(json.dumps(loader.get_corpus_stats(), indent=2))
