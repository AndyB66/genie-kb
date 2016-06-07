import random
from model.query import *


class BatchSampler:

    def __init__(self, fact_kb, batch_size, which_set="TAC_ET:2014_train", max_contexts=-1):
        self.fact_kb = fact_kb
        self.kb = fact_kb.kb
        self.batch_size = batch_size
        self.which_set = which_set
        self.num_contexts = self.kb.num_contexts(which_set)
        if max_contexts > 0:
            self.num_contexts = min(max_contexts, self.num_contexts)
        self.epoch_size = self.num_contexts // self.batch_size
        self._rng = random.Random(73642)
        self.reset()

    def reset(self):
        self.todo = list(range(self.num_contexts))
        self._rng.shuffle(self.todo)
        if self.num_contexts % self.batch_size != 0:
            self.todo = self.todo[:-(self.num_contexts % self.batch_size)]
        self.count = 0

    def end_of_epoch(self):
        return self.count == self.epoch_size

    def __iter__(self):
        return self

    def next(self):
        if self.count >= self.epoch_size:
            raise StopIteration
        return self.get_batch()

    def get_batch(self):
        '''
        Note, the data in the kb is structured as follows: contexts= supporting_evidence + "||" + query.
        Thus, we have to split contexts.
        :return: list of (contexts, query_positions, negative_candidates, supporting_facts)
        '''
        if self.end_of_epoch():
            print("WARNING: End of epoch reached in sampler. Resetting automatically.")
            self.reset()

        batch_queries = []
        for i in range(self.batch_size):
            ctxt = self.kb.context(self.todo[i], self.which_set)
            starts, ends = self.kb.spans(self.todo[i], self.which_set)
            answers = self.kb.answers(self.todo[i], self.which_set)
            # use fact_kb entity ids as answers, not the whole vocabulary
            answers = [self.fact_kb.id(self.kb.vocab[x]) for x in answers]
            #supp_queries = []
            #for i in range(len(starts)):
                #supp_queries.append(ContextQuery(None, starts[i], ends[i], answers[i], None))
            #supp_queries = ContextQueries(None, supp_queries)
            neg_cands = list(set((c for c in answers if c != answers[-1])))
            query = ContextQuery(ctxt, starts[-1], ends[-1], answers[-1], neg_cands, supporting_evidence=[supp_queries])
            batch_queries.append(ContextQueries(ctxt, [query]))
        self.todo = self.todo[self.batch_size:]
        self.count += 1
        return batch_queries

    def get_epoch(self):
        return self.count / self.epoch_size