from operator import index
import torch
from torch import nn
from typing import Any, Dict, Union
from trainers.seq2seq_trainer_nomoe import Seq2SeqTrainer

from packaging import version

_use_native_amp = False
_use_apex = False

# Check if Pytorch version >= 1.6 to switch between Native AMP and Apex
if version.parse(torch.__version__) < version.parse("1.6"):
    from transformers.file_utils import is_apex_available

    if is_apex_available():
        from apex import amp
    _use_apex = True
else:
    _use_native_amp = True
    from torch.cuda.amp import autocast


class OriSeq2SeqTrainer(Seq2SeqTrainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def _training_step(self, model: nn.Module, inputs: Dict[str, Union[torch.Tensor, Any]], optimizer) -> torch.Tensor:
        self.B, self.L = inputs['labels'].shape
        self.pad_mask = (inputs['labels'] == self.config.pad_token_id).view(self.B, 1, self.L).to(self.args.device)
        inputs = self._prepare_inputs(inputs)
        model.train()
        loss = self.compute_loss(model, inputs)
        if self.args.gradient_accumulation_steps > 1:
            loss = loss / self.args.gradient_accumulation_steps

        if self.args.fp16 and _use_native_amp:
            self.scaler.scale(loss).backward()
        elif self.args.fp16 and _use_apex:
            with amp.scale_loss(loss, self.optimizer) as scaled_loss:
                scaled_loss.backward()
        else:
            loss.backward()

        return loss.detach()

    def compute_loss(self, model, inputs):
        labels = inputs.pop("labels")
        input_ids = inputs["input_ids"]
        outputs = model(**inputs, use_cache=False)
        logits = outputs[0]
        return self._compute_loss(logits=logits, encoder_outputs=outputs[1], encoder_sent_outputs=outputs[2],
                                  encoder_target_outputs=outputs[3], sent_outputs=outputs[4], labels=labels,
                                  input_ids=input_ids)