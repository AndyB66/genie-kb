import numpy as np
import sys

def rank_batch(sess, model, batch):
    contexts, positions, neg_candidates, supporting_evidence = batch
    scores = model.score_examples_with_negs(sess, contexts, positions, neg_candidates, supporting_evidence)
    ix = np.argsort(scores, 1)[:,::-1]
    rank = np.where(ix == 0)[1] + 1

    return rank


def eval_dataset(sess, model, sampler, verbose=False):
    sampler.reset()
    total = 0
    tp = 0
    rr = 0
    while not sampler.end_of_epoch():
        batch = sampler.get_batch()
        ranked = rank_batch(sess, model, batch)
        tp += np.where(ranked == 1)[0].size
        total += ranked.size
        rr += np.sum(1.0 / ranked)
        if verbose:
            sys.stdout.write("\r%.1f%%, acc: %.3f, mrr: %.3f" % (sampler.get_epoch()*100.0, tp / total, rr / total))
            sys.stdout.flush()


    acc = tp / total
    mrr = rr / total

    if verbose:
        print("Accuracy: %.3f" % acc)
        print("MRR: %.3f" % mrr)

    return acc, mrr

