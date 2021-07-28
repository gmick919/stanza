"""
Converts the FIRE 2013 dataset to TSV

http://au-kbc.org/nlp/NER-FIRE2013/index.html

The dataset is in six tab separated columns.  The columns are

word tag chunk ner1 ner2 ner3

This script keeps just the word and the ner1.  It is quite possible that using the tag would help
"""

import argparse
import glob
import os
import random

def normalize(e1, e2, e3):
    if e1 == 'o':
        return "O"

    if e2 != 'o' and e1[:2] != e2[:2]:
        raise ValueError("Found a token with conflicting position tags %s,%s" % (e1, e2))
    if e3 != 'o' and e2 == 'o':
        raise ValueError("Found a token with tertiary label but no secondary label %s,%s,%s" % (e1, e2, e3))
    if e3 != 'o' and (e1[:2] != e2[:2] or e1[:2] != e3[:2]):
        raise ValueError("Found a token with conflicting position tags %s,%s,%s" % (e1, e2, e3))

    if e1[2:] in ('ORGANIZATION', 'ENTERTAINMENT', 'FACILITIES'):
        return e1
    if e1[2:] == 'DISEASE' and e2 == 'o':
        return e1
    if e1[2:] == 'PLANTS' and e2[2:] != 'PARTS':
        return e1
    if e1[2:] == 'PERSON' and e2[2:] == 'INDIVIDUAL':
        return e1
    if e1[2:] == 'LOCATION' and (e2[2:] == 'PLACE' or (e2[2:] == 'ADDRESS' and e3[2:] == 'STNAME')):
        return e1
    if e1[2:] in ('DATE', 'TIME', 'YEAR', 'MONTH'):
        string = e1[:2] + 'DATE/TIME'
        return string

    return "O"

def convert_fileset(output_csv_file, filenames):
    # first, read the sentences from each data file
    sentences = []
    for filename in filenames:
        with open(filename) as fin:
            next_sentence = []
            for line in fin:
                line = line.strip()
                if not line:
                    # lots of single line "sentences" in the dataset
                    if next_sentence:
                        if len(next_sentence) > 1:
                            sentences.append(next_sentence)
                        next_sentence = []
                else:
                    next_sentence.append(line)
            if next_sentence and len(next_sentence) > 1:
                sentences.append(next_sentence)
    with open(output_csv_file, "w") as fout:
        for sentence in sentences:
            for line in sentence:
                pieces = line.split("\t")
                if len(pieces) != 6:
                    raise ValueError("Found %d pieces instead of the expected 6" % len(pieces))
                if pieces[3] == 'o' and (pieces[4] != 'o' or pieces[5] != 'o'):
                    raise ValueError("Inner NER labeled but the top layer was O")
                fout.write("%s\t%s\n" % (pieces[0], normalize(pieces[3], pieces[4], pieces[5])))
            fout.write("\n")

def convert_fire_2013(input_path, train_csv_file, dev_csv_file, test_csv_file):
    filenames = glob.glob(os.path.join(input_path, "*"))

    # won't be numerically sorted... shouldn't matter
    filenames = sorted(filenames)
    random.shuffle(filenames)
    train_cutoff = int(0.8 * len(filenames))
    dev_cutoff = int(0.9 * len(filenames))

    train_files = filenames[:train_cutoff]
    dev_files   = filenames[train_cutoff:dev_cutoff]
    test_files  = filenames[dev_cutoff:]

    assert len(train_files) > 0
    assert len(dev_files) > 0
    assert len(test_files) > 0

    convert_fileset(train_csv_file, train_files)
    convert_fileset(dev_csv_file,   dev_files)
    convert_fileset(test_csv_file,  test_files)
    
if __name__ == '__main__':
    random.seed(1234)

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default="/home/john/extern_data/ner/FIRE2013/hindi_train",  help="Directory with raw files to read")
    parser.add_argument('--train_file', type=str, default="/home/john/stanza/data/ner/hi_fire2013.train.csv", help="Where to put the train file")
    parser.add_argument('--dev_file',   type=str, default="/home/john/stanza/data/ner/hi_fire2013.dev.csv",   help="Where to put the dev file")
    parser.add_argument('--test_file',  type=str, default="/home/john/stanza/data/ner/hi_fire2013.test.csv",  help="Where to put the test file")
    args = parser.parse_args()

    convert_fire_2013(args.input_path, args.train_file, args.dev_file, args.test_file)
