import os
import numpy as np
from collections import defaultdict

from nlgeval import compute_metrics
from nlgeval import compute_individual_metrics as compute_individual

def get_all_files(path):

    if os.path.isfile(path): return [path]

    return [f for d in os.listdir(path)
              for f in get_all_files(os.path.join(path, d))]
    

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