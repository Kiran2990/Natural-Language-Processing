import string
import math
import re

text = ''
bigram_dict = {}
trigram_dict = {}
previous_char = ''
probabilityDict = {}


def load_format_file():
    global text
    sample = open('sample.txt', 'r')
    with sample as fileinput:
        for line in fileinput:
            text += line.lower()

    text = text.translate(None, string.punctuation)
    text = text.replace('\n', '').replace('\t', '')
    text = re.sub('\s+', ' ', text)


def get_value_from_dict(key, dict):
    if not key in dict:
        return 0
    return dict[key]


def probability(c1, c2c3):
    c2c3c1 = c2c3 + c1
    count_c2c3c1 = trigram_dict[c2c3c1]
    count_c2c3 = bigram_dict[c2c3]
    prob = (float(count_c2c3c1) + 0.1) / (count_c2c3 + (0.1 * 37))
    return prob


def generate_bigram_dict(text):
    bi_dict = {}
    i = 0
    while i < len(text):
        bigram = text[i:i + 2]
        i += 1
        bi_dict.update({bigram: get_value_from_dict(bigram, bi_dict) + 1})
    return bi_dict


def generate_trigram_dict(text):
    tri_dict = {}
    i = 0
    while i < len(text):
        trigram = text[i:i + 3]
        i += 1
        tri_dict.update({trigram: get_value_from_dict(trigram, tri_dict) + 1})
    return tri_dict

load_format_file()
bigram_dict = generate_bigram_dict(text)
trigram_dict = generate_trigram_dict(text)

i = 0
for character in text:
    previous_char += character
    if not i < 2:
        probabilityDict.update({character + previous_char[:2]: probability(character, previous_char[:2])})
        previous_char = previous_char[1:]
    i += 1


sentence1 = 'he somehow made this analogy sound exciting instead of hopeless'
sentence2 = 'no living humans had skeletal features remotely like these'
sentence3 = 'frequent internet and social media users do not have higher stress levels'
sentence4 = 'the sand the two women were sweeping into their dustpans was transferred into plastic bags'


def cross_entropy(sentence):
    line_bigram_dict = generate_bigram_dict(sentence)
    line_trigram_dict = generate_trigram_dict(sentence)
    entropy = 0
    previous_char = ''
    i = 0
    for character in sentence:
        previous_char = previous_char + character
        if not i < 2:
            p = float(line_trigram_dict[previous_char[:2]+character] + 0.1)/( \
                line_bigram_dict[previous_char[:2]] + 0.1 * 37)
            if character + previous_char[:2] not in probabilityDict.keys():
                prob = float(0 + 0.1) / (0.1 * 37)
            else:
                prob = probabilityDict[character + previous_char[:2]]
            entropy += (p * math.log(prob,2))
            previous_char = previous_char[1:]
        i += 1
    return entropy/(len(sentence)-2) * -1

print 'Entropy of Sentence 1: ', cross_entropy(sentence1)
print 'Entropy of Sentence 2: ', cross_entropy(sentence2)
print 'Entropy of Sentence 3: ', cross_entropy(sentence3)
print 'Entropy of Sentence 4: ', cross_entropy(sentence4)
