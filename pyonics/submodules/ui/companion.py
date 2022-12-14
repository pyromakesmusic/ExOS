import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

sequence = '''You can't smoke tonight, you get way too live
And you can't drink tonight, you get fucked up sometimes
You and I, I lose every fight
We blur every line, and risk it every time
Girl, who do you blame?
Blame me
I never start a fight, I man up every time
Girl, who do you blame?
Blame me, blame me, no, blame me
Girl, who do you blame?
I'm single, I'm faithful
I'm young, and I'm able
Real ones on my payroll
I'm signed to my label
She's Queen and I'm Pharaoh
For her I'd empty my barrel
Timbs' on, with her hair low
Real cute, but still ghetto, I'''

inputs = tokenizer.encode(sequence, return_tensors='pt')
outputs = model.generate(inputs, max_length=200, do_sample=True)
text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(text)