import logging
import os, sys
import json
import torch
from dataclasses import dataclass, field
from typing import Optional

from transformers import (
    HfArgumentParser,
    TrainingArguments,
    set_seed,
)

print(1)
from evals.eval_acc_div import eval_accuracy_diversity

print(2)
from transformers.trainer_utils import EvaluationStrategy
from trainers.trainer_utils import (
    assert_all_frozen,
    freeze_embeds,
    freeze_params,
    lmap,
    save_json,
    use_task_specific_params,
    write_txt_file,
)

logger = logging.getLogger(__name__)


@dataclass
class Seq2SeqTrainingArguments(TrainingArguments):
    label_smoothing: Optional[float] = field(default=0.0,
                                             metadata={"help": "The label smoothing epsilon to apply (if not zero)."})
    sortish_sampler: bool = field(default=False, metadata={"help": "Whether to SortishSamler or not."})
    predict_with_generate: bool = field(default=False, metadata={
        "help": "Whether to use generate to calculate generative metrics (ROUGE, BLEU)."})
    adafactor: bool = field(default=False, metadata={"help": "whether to use adafactor"})
    encoder_layerdrop: Optional[float] = field(default=None, metadata={
        "help": "Encoder layer dropout probability. Goes into model.config."})
    decoder_layerdrop: Optional[float] = field(default=None, metadata={
        "help": "Decoder layer dropout probability. Goes into model.config."})
    dropout: Optional[float] = field(default=None, metadata={"help": "Dropout probability. Goes into model.config."})
    attention_dropout: Optional[float] = field(default=None, metadata={
        "help": "Attention dropout probability. Goes into model.config."})
    gradient_accumulation_steps: Optional[int] = field(default=6,
                                                       metadata={
                                                           "help": "The maximum total sequence length for target text after tokenization. Sequences longer "
                                                                   "than this will be truncated, sequences shorter will be padded."}, )
    device: Optional[str] = field(default="cuda:0", metadata={
        "help": "The maximum total sequence length for target text after tokenization. Sequences longer "})


@dataclass
class ModelArguments:
    model_name_or_path: str = field(
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"})
    model_type: str = field(metadata={"help": "Model type from list [vae, moe, sampling, ...]"})
    config_name: Optional[str] = field(default=None, metadata={
        "help": "Pretrained config name or path if not the same as model_name"})
    tokenizer_name: Optional[str] = field(default=None, metadata={
        "help": "Pretrained tokenizer name or path if not the same as model_name"})
    cache_dir: Optional[str] = field(default=None, metadata={
        "help": "Where do you want to store the pretrained models downloaded from s3"})
    freeze_encoder: bool = field(default=False, metadata={"help": "Whether tp freeze the encoder."})
    freeze_embeds: bool = field(default=False, metadata={"help": "Whether  to freeze the embeddings."})


@dataclass
class DataTrainingArguments:
    data_dir: str = field(
        metadata={"help": "The input data dir. Should contain the .tsv files (or other data files) for the task."})
    task: Optional[str] = field(default="summarization",
                                metadata={
                                    "help": "Task name, summarization (or summarization_{dataset} for pegasus) or translation"}, )
    max_source_length: Optional[int] = field(default=512,
                                             metadata={
                                                 "help": "The maximum total input sequence length after tokenization. Sequences longer "
                                                         "than this will be truncated, sequences shorter will be padded."}, )
    max_target_length: Optional[int] = field(default=128,
                                             metadata={
                                                 "help": "The maximum total sequence length for target text after tokenization. Sequences longer "
                                                         "than this will be truncated, sequences shorter will be padded."}, )
    val_max_target_length: Optional[int] = field(default=128,
                                                 metadata={
                                                     "help": "The maximum total sequence length for validation target text after tokenization. Sequences longer "
                                                             "than this will be truncated, sequences shorter will be padded."}, )
    test_max_target_length: Optional[int] = field(default=128,
                                                  metadata={
                                                      "help": "The maximum total sequence length for test target text after tokenization. Sequences longer "
                                                              "than this will be truncated, sequences shorter will be padded."}, )
    n_train: Optional[int] = field(default=None, metadata={"help": "# training examples. -1 means use all."})
    n_val: Optional[int] = field(default=None, metadata={"help": "# validation examples. -1 means use all."})
    n_test: Optional[int] = field(default=None, metadata={"help": "# test examples. -1 means use all."})
    src_lang: Optional[str] = field(default=None, metadata={"help": "Source language id for translation."})
    tgt_lang: Optional[str] = field(default=None, metadata={"help": "Target language id for translation."})
    eval_beams: Optional[int] = field(default=None, metadata={"help": "# num_beams to use for evaluation."})

    # For sampling methods
    top_k: Optional[int] = field(default=0,
                                 metadata={"help": "keep only top k tokens with highest probability (top-k filtering)"})
    top_p: Optional[float] = field(default=1.0, metadata={
        "help": "keep the top tokens with cumulative probability >= top_p (nucleus filtering)"})
    do_sample: Optional[bool] = field(default=False, metadata={"help": "# Do sampling (multinomial/neclus sampling)."})
    # For MoE methods
    mixtures: Optional[int] = field(default=3, metadata={"help": "number of experts in the model"})
    prompt_nums: Optional[int] = field(default=5, metadata={"help": "number of experts propmt ids"})
    mixture_embedding: Optional[bool] = field(default=False)
    expert_id: Optional[int] = field(default=5e4, metadata={"help": "specify a token as expert token"})
    alpha: Optional[float] = field(default=1)
    beta: Optional[float] = field(default=0.5)


def main():
    print(3)
    parser = HfArgumentParser((ModelArguments, DataTrainingArguments, Seq2SeqTrainingArguments))

    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        model_args, data_args, training_args = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))
    else:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    from trainers.trainer_utils import LegacySeq2SeqDataset, Seq2SeqDataCollator
    from transformers import BartConfig
    from sources.moe.modeling_bart import BartMoEForConditionalGeneration as BartModel
    from trainers.moe_trainer import MoESeq2SeqTrainer as Seq2SeqTrainer
    from transformers import BartTokenizer
    # n_sample for evluating the models during training
    training_args.eval_beams = data_args.eval_beams
    training_args.data_dir = data_args.data_dir

    # Ensure output dir is not existed
    if (
            os.path.exists(training_args.output_dir) and os.listdir(training_args.output_dir)
            and training_args.do_train and not training_args.overwrite_output_dir
    ):
        raise ValueError(
            f"Output directory ({training_args.output_dir}) already exists and is not empty. Use --overwrite_output_dir to overcome."
        )

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO if training_args.local_rank in [-1, 0] else logging.WARN,
    )

    logger.warning(
        "Process rank: %s, device: %s, n_gpu: %s, distributed training: %s, 16-bits training: %s",
        training_args.local_rank, training_args.device, training_args.n_gpu,
        bool(training_args.local_rank != -1), training_args.fp16,
    )

    set_seed(training_args.seed)

    config = BartConfig.from_pretrained(
        model_args.config_name if model_args.config_name else model_args.model_name_or_path,
        cache_dir=model_args.cache_dir, mirror='tuna',
    )

    extra_model_params = ("encoder_layerdrop", "decoder_layerdrop", "dropout", "attention_dropout")
    for p in extra_model_params:
        if getattr(training_args, p, None):
            assert hasattr(config, p), f"({config.__class__.__name__}) doesn't have a `{p}` attribute"
            setattr(config, p, getattr(training_args, p))

    tokenizer = BartTokenizer.from_pretrained(
        model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
    )

    data_args.expert_prompt = torch.randint(
        low=1, high=len(tokenizer), size=(data_args.mixtures, data_args.prompt_nums))
    # data_args.expert_prompt = torch.tensor([40437,  1472, 13794,  2706]).unsqueeze(0)
    config.mixtures = data_args.mixtures
    config.mixture_embedding = data_args.mixture_embedding

    model = BartModel.from_pretrained(
        model_args.model_name_or_path,
        config=config,
        cache_dir=model_args.cache_dir,
    )

    use_task_specific_params(model, data_args.task)

    # set num_beams for evaluation
    if data_args.eval_beams is None:
        data_args.eval_beams = model.config.num_beams

    if model_args.freeze_embeds:
        freeze_embeds(model)
    if model_args.freeze_encoder:
        freeze_params(model.get_encoder())
        assert_all_frozen(model.get_encoder())

    # Get datasets
    train_dataset = (
        LegacySeq2SeqDataset(
            tokenizer=tokenizer,
            type_path="train",
            data_dir=data_args.data_dir,
            n_obs=data_args.n_train,
            max_target_length=data_args.max_target_length,
            max_source_length=data_args.max_source_length,
            prefix=model.config.prefix or "",
        )
        if training_args.do_train
        else None
    )
    eval_dataset = (
        LegacySeq2SeqDataset(
            tokenizer=tokenizer,
            type_path="val",
            data_dir=data_args.data_dir,
            n_obs=data_args.n_val,
            max_target_length=data_args.val_max_target_length,
            max_source_length=data_args.max_source_length,
            prefix=model.config.prefix or "",
        )
        if training_args.do_eval or training_args.evaluation_strategy != EvaluationStrategy.NO
        else None
    )
    trainer = Seq2SeqTrainer(
        model=model,
        config=config,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=Seq2SeqDataCollator(tokenizer, data_args, training_args.tpu_num_cores),
        data_args=data_args,
    )

    # Training (eval during each epoch)
    if training_args.do_train:
        trainer.train(
            model_path=model_args.model_name_or_path if os.path.isdir(model_args.model_name_or_path) else None)


if __name__ == "__main__":
    main()
