import random
import json
import torch

import torch
import torch.nn as nn

class NeuralNet(nn.Module):
	def __init__(self, input_size, hidden_size, num_classes):
		super(NeuralNet, self).__init__()
		self.l1 = nn.Linear(input_size, hidden_size)
		self.l2 = nn.Linear(hidden_size, hidden_size)
		self.l3 = nn.Linear(hidden_size, num_classes)
		self.relu = nn.ReLU()

	def forward(self, x):
		out = self.l1(x)
		out = self.relu(out)
		out = self.l2(out)
		out = self.relu(out)
		out = self.l3(out)
		return out

import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer

nltk.download('punkt')
stemmer = PorterStemmer()

def tokenize(sentence):
	return nltk.word_tokenize(sentence, language='portuguese')

def stem(word):
	return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, all_words):
	tokenized_sentence = [stem(w) for w in tokenized_sentence]

	bag = np.zeros(len(all_words), dtype=np.float32)
	for idx, w in enumerate(all_words):
		if w in tokenized_sentence:
			bag[idx] = 1.0
	return bag

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

if __name__ == "__main__":
    database_directory=''
else:
    database_directory='modules/'

with open('{}intends.json'.format(database_directory), 'r') as f:
	intents = json.load(f)

file_name = "{}data.pth".format(database_directory)
data = torch.load(file_name)

input_size = data["input_size"]
output_size = data["output_size"]
hidden_size = data["hidden_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Byte"

def get_response(sentence):

	sentence = tokenize(sentence)
	X = bag_of_words(sentence, all_words)
	X = X.reshape(1, X.shape[0])
	X = torch.from_numpy(X)

	output = model(X)
	_, predicted = torch.max(output, dim=1)

	tag = tags[predicted.item()]

	probs = torch.softmax(output, dim=1)
	prob = probs[0][predicted.item()]
	print(prob.item())
	if prob.item() > 0.99:
		for intent in intents["intents"]:
			if tag == intent["tag"]:
				return random.choice(intent['responses'])

	return "error"

if __name__ == "__main__":
    print("(type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)
