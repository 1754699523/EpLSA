########################
#### Run experiment
########################

DATASET=${}
INPUT_DIR=${}
OUTPUT_DIR=${}

option="
    --data_dir data/anlg
    --model_name_or_path anlg/checkpoint_best_dev
    --model_type moe
    --output_dir anlg
    --max_source_length 40
    --max_target_length 40
    --val_max_target_length 40
    --test_max_target_length 40
    --do_predict
    --eval_beams 3
    --per_device_train_batch_size 15
    --per_device_eval_batch_size 15
    --metric_for_best_model topk_bleu_4
    --predict_with_generate
    --load_best_model_at_end
    --overwrite_output_dir
    --evaluate_during_training
"

cmd="python predict.py ${option}"

echo $cmd
eval $cmd