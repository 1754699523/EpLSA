import os
import numpy as np
from collections import defaultdict

from nlgeval import compute_metrics
from nlgeval import compute_individual_metrics as compute_individual

def get_all_files(path):

    if os.path.isfile(path): return [path]

    return [f for d in os.listdir(path)
              for f in get_all_files(os.path.join(path, d))]
    
def eval_topk_acc(hyp_path, ref_path, step):

    with open(hyp_path, 'r') as hyp_file, open(ref_path, 'r') as ref_file:
        hyps = hyp_file.readlines()
        refs = ref_file.readlines()

        hyps_topk = [hyps[i: i+step] for i in range(0, len(hyps), step)]
        hyps_best = []
        for hyp, ref in zip(hyps_topk, refs):
            hyp_score_list = [compute_individual(ref, h)['bleu_4'] for h in hyp]
            hyps_best.append(hyp[np.argmax(hyp_score_list)])
        
        topk_metrics = compute_metrics(ref_list=refs, hyp_list=hyps_best)
        topk_metrics = {f'topk_{k}': v for k, v in topk_metrics.items()}

        return topk_metrics


def eval_self_bleu(hyp_path, step):

    with open(hyp_path, 'r') as hyp_file:
        hyps = hyp_file.readlines()
        hyps_topk = [hyps[i: i+step] for i in range(0, len(hyps), step)]

        hyp_list, ref_list = [], []
        for hyps in hyps_topk:
            for i in range(len(hyps)):
                hyp_list.append(hyps[i])
                ref_list.append('\t'.join(hyps[:i]+hyps[i+1:]))
        self_metrics = compute_metrics(hyp_list=hyp_list, ref_list=ref_list)
        self_metrics = {f'self_{k}': v for k, v in self_metrics.items()}
        return self_metrics



def eval_accuracy_diversity(hyp_path, ref_path, step):

    metrics = {}
    metrics.update(eval_topk_acc(hyp_path, ref_path,step))
    metrics.update(eval_self_bleu(hyp_path, step))
    return metrics

