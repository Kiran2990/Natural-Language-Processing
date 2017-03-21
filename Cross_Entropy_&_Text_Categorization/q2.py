import collections
import string
import re
import os
import math

all_play_words = {}  # A dictionary with file_name : all words in file as list of words
comedy_files = []  # A list of all comedy file names
tragedy_files = []  # A list of all tragedy file names
mainVocabularySet = []  # A list of the vocabulary set which is generated and refined
all_comedy_files_text = []  # A list of all the words in all comedy files
all_tragedy_files_text = []  # A list of all the words in all tragedy files

comedyLikeTragedy = {}  # A dictionary to find which comedy play is more like tragedy, file:log likelihood
tragedyLikeComedy = {}  # A dictionary to find which tragedy play is more like comedy, file:log likelihood


def tokenize(file_name):
    text = ''
    sample = open(file_name, 'r')
    with sample as fileinput:
        for line in fileinput:
            text += line.lower()
    text = text.translate(None, string.punctuation)
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = re.sub('\s+', ' ', text).split(' ')
    return text


def get_value_from_dict(key, dictonary):
    if not key in dictonary:
        return 0
    return dictonary[key]


def build_play_set(directory_path):
    global all_play_words
    for root, dirs, files in os.walk(directory_path):
        for f in files:
            if f.endswith('.txt'):
                play = tokenize(root + '/' + f)
                all_play_words.update({f: play})


def build_vocab_set():
    textList = []
    for key, items in all_play_words.items():
        textList.extend(items)
    vocab = collections.Counter(textList)
    vocabSet = (word for word in vocab.keys() if vocab[word] >= 5)
    return list(vocabSet)


def build_all_occurrences(vocab):
    all_play_words_occurance = {}
    for word in vocab:
        for key, item in all_play_words.items():
            if word in item:
                all_play_words_occurance.update({word: get_value_from_dict(word, all_play_words_occurance) + 1})

    for key, item in all_play_words_occurance.items():
        if item < 2:
            all_play_words_occurance.pop(key)
    return all_play_words_occurance


def build_training_sets(exempt_file):
    comedy_list, tragedy_list = [], []
    for file in comedy_files:
        if file in all_play_words.keys() and not file == exempt_file:
            comedy_list.extend(all_play_words[file])

    for file in tragedy_files:
        if file in all_play_words.keys() and not file == exempt_file:
            tragedy_list.extend(all_play_words[file])

    return comedy_list, tragedy_list


def compute_probabilities(comdey_list, tragedy_list, test_file_list):
    comedy_probability = math.log(0.5, 2)
    tragedy_probability = math.log(0.5, 2)
    wordSet = set(vocabulary).intersection(set(test_file_list))
    for word in wordSet:
        wordTimes = test_file_list.count(word)
        comedy_probability += math.log(float(comdey_list.count(word) + 0.1) / (len(comdey_list) \
                                                                               + 0.1 * len(vocabulary)), 2) * wordTimes
        tragedy_probability += math.log((float(tragedy_list.count(word)) + 0.1) / (len(tragedy_list) \
                                                                                   + 0.1 * len(vocabulary)),
                                        2) * wordTimes
    return comedy_probability, tragedy_probability


def write_to_file(file_name, org_genre, pre_genre, likely_hood):
    print_string = 'Play_Name:' + file_name + '  Original_Genre:' + org_genre + '  Model_Predicted_Genre:' \
                   + pre_genre + '  Likelihood_Ratio: ' + likely_hood
    classification_file.write(print_string + '\n')
    print print_string


def compute_top_comic_tragic_features():
    top_comedy_features = open('Top_20_Comic_features.txt', 'w')
    top_tragic_features = open('Top_20_Tragic_features.txt', 'w')
    top_comedy_features.write('Feature : LikelyHood Ratio \n')
    top_tragic_features.write('Feature : LikelyHood Ratio \n')
    for word in vocabulary:
        comedy_probability = float(all_comedy_files_text.count(word) + 0.1) / (len(all_comedy_files_text) \
                                                                               + 0.1 * len(vocabulary))
        tragedy_probability = float(all_tragedy_files_text.count(word) + 0.1) / (len(all_tragedy_files_text) \
                                                                                 + 0.1 * len(vocabulary))
        likely = math.log((comedy_probability / tragedy_probability), 2)

        likelyHood.update({word: likely})

    orderedLikelyHood = collections.OrderedDict(sorted(likelyHood.items(), key=lambda x: x[1], ))

    print 'Tragic Features'
    for i in range(20):
        key, item = orderedLikelyHood.popitem(False)
        top_tragic_features.write(key + ' : ' + str(item) + '\n')
        print key, ':', item

    print 'Comic Features'
    for i in range(20):
        key, item = orderedLikelyHood.popitem()
        top_comedy_features.write(key + ' : ' + str(item) + '\n')
        print key, ':', item

    top_comedy_features.close()
    top_tragic_features.close()


def compute_model_prediction(is_comedy):
    if is_comedy:
        for c_file in comedy_files:
            all_comedy_files_text.extend(all_play_words[c_file])
            comedy_word_list, tragedy_word_list = build_training_sets(c_file)
            test_file_list = list(all_play_words[c_file])
            p_comedy, p_tragedy = compute_probabilities(comedy_word_list, tragedy_word_list, test_file_list)
            if p_comedy > p_tragedy:
                genre = 'Comedy'
            else:
                genre = 'Tragedy'
            likelyHoodRatio = p_comedy - p_tragedy
            write_to_file(c_file, 'Comedy', genre, str(likelyHoodRatio))
            comedyLikeTragedy.update({c_file: abs(p_tragedy) - abs(p_comedy)})

        print 'Comedy most like a Tragedy:', min(comedyLikeTragedy.items(), key=lambda x: x[1])[0]
        classification_file.write(
            '\n Comedy most like a Tragedy: ' + min(comedyLikeTragedy.items(), key=lambda x: x[1])[0])
    else:
        for t_file in tragedy_files:
            all_tragedy_files_text.extend(all_play_words[t_file])
            comedy_word_list, tragedy_word_list = build_training_sets(t_file)
            test_file_list = list(all_play_words[t_file])
            p_comedy, p_tragedy = compute_probabilities(comedy_word_list, tragedy_word_list, test_file_list)
            if p_comedy > p_tragedy:
                genre = 'Comedy'
            else:
                genre = 'Tragedy'
            likelyHoodRatio = p_comedy - p_tragedy
            write_to_file(t_file, 'Tragedy', genre, str(likelyHoodRatio))
            tragedyLikeComedy.update({t_file: abs(p_comedy) - abs(p_tragedy)})

        print 'Tragedy most like a Comedy:', min(tragedyLikeComedy.items(), key=lambda x: x[1])[0]
        classification_file.write(
            '\n Tragedy most like a Comedy: ' + min(tragedyLikeComedy.items(), key=lambda x: x[1])[0])


for root, dirs, files in os.walk('shakespeare/comedies'):
    for f in files:
        comedy_files.append(f)

for root, dirs, files in os.walk('shakespeare/tragedies'):
    for f in files:
        tragedy_files.append(f)

print 'Computing Vocabulary set'

build_play_set('shakespeare/')
mainVocabularySet = build_vocab_set()
vocab_set = build_all_occurrences(mainVocabularySet)
vocabulary = list(vocab_set)
print 'Vocabulary set Built'
vocabFile = open('Vocabulary_list.txt', 'w')
for word in vocabulary:
    vocabFile.write(word + '\n')
print 'Vocabulary File write completed'
vocabFile.close()
print 'Number of words in Vocabulary set: ', len(vocabulary)

print 'Classification Started'

classification_file = open('Play_Classification.txt', 'w')
classification_file.write('Classification for Comedy plays \n\n')
compute_model_prediction(True)
print 'Classification comedy completed'

classification_file.write('\n\nClassification for Tragedy plays \n\n')
compute_model_prediction(False)
print 'Classification tragedy completed'

classification_file.close()

likelyHood = {}

for c_file in comedy_files:
    all_comedy_files_text.extend(all_play_words[c_file])

for t_file in tragedy_files:
    all_tragedy_files_text.extend(all_play_words[t_file])

print 'Computing Top 20 Comic/Tragic features'

compute_top_comic_tragic_features()

print 'Program Completed. Please check the files generated'
