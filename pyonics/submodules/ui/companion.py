import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class Companion:
    def chat(self):
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        model = GPT2LMHeadModel.from_pretrained('gpt2')

        go_flag = True
        sequence = '''This is placeholder text that should be filled with useful operational information'''
        inputs = tokenizer.encode(sequence, return_tensors='pt')
        outputs = model.generate(inputs, max_length=200, do_sample=True)
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(text)

    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.go_flag = True

        while self.go_flag == True:

            sequence = input()
            if sequence == "":
                self.go_flag == False
            else:
                inputs = tokenizer.encode(sequence, return_tensors='pt')
                outputs = model.generate(inputs, max_length=200, do_sample=True)
                text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(text)