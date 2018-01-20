
import argparse
argparser = argparse.ArgumentParser("python3 parad2aligned2zerofilled.py",
                                    description="Aligns a set of word forms with morph boundaries")
argparser.add_argument("-i", "--segmented-words",
                        default="inari-segm.csv",
                        help="moprheme names and the segmented example word forms as a CSV file")
argparser.add_argument("-o", "--aligned-words",
                        default="inari-aligned.csv",
                        help="example words plus zero-filled aligned forms as a CSV file")
argparser.add_argument("-s", "--morph-separator",
                        default=".",
                        help="separator between morphs in the word form")
argparser.add_argument("-d", "--csv-delimiter",
                        default=",",
                        help="delimiter between the two fields")
argparser.add_argument("-n", "--name-separator",
                        default=" ",
                        help="separator between morpheme names in the morpheme list")
argparser.add_argument("-z", "--zero-symbol",
                        default="Ø",
                        help="symbol to be inserted in word forms in order to align them")
args = argparser.parse_args()

# STEP 1:
# Read in the segmented words and collect the allomorphs of each morpheme

import re, csv
from orderedset import OrderedSet
import collections


# all allomorphs are collected into the following dict where
# index: morpheme name, value: allomorphs as an ordered set
morph_set = {} 

# all example words are collected into the following list where
# each word is represented as a list of (morpheme,morph) pairs
seg_example_list = []

csvfile = open(args.segmented_words)
csv.excel.delimiter = args.csv_delimiter
reader = csv.DictReader(csvfile)
i = 0
morph_set = {}
for row in reader:
    #print(row)###
    morpheme_list = row["MORPHEMES"].strip().split(args.name_separator)
    #print(row["MORPHEMES"])###
    #print(len(morpheme_list))###
    morph_list = row["MORPHS"].strip().split(args.morph_separator)
    #print(morph_list)###
    i = i + 1
    if len(morpheme_list) != len(morph_list):
        print("** line", i, ":", row['MORPHEMES'],
                "is incompatible with", row["MORPHS"])
        continue
    pair_list = list(zip(morpheme_list, morph_list))
    seg_example_list.append(pair_list)
    for morpheme, morph in pair_list:
        if morpheme not in morph_set:
            morph_set[morpheme] = OrderedSet()
        morph_set[morpheme].add(morph.strip())
csvfile.close()

#print("----morph_set:", morph_set)###
#print("----seg_example_list:", seg_example_list)###

# STEP 2:
# align the allomorphs of each morpheme

import sys
#sys.path.insert(0, "/Users/koskenni/github/alignment/")
from multialign import aligner

alignments = {} # index: morpheme name, value: sequence of aligned symbols 
morphs = {}
vowels = 'aeiouyäö'
l = len(vowels)

for morpheme in sorted(morph_set.keys()):
    morphs[morpheme] = list(morph_set[morpheme])
    words = list(morph_set[morpheme])
    #print("words:", words)###
    aligned_sym_seq = aligner(words,
                                  2, morpheme, verbosity=1,
                                  max_weight_allowed=10000.0)
    #print("aligned_sym_seq:", aligned_sym_seq)###
    alignments[morpheme] = aligned_sym_seq

#print("----alignments:", alignments)###

# STEP 3:
# Compute the zero filled morphs out of the sequences of aligned symbols

# in the following, index: (morpheme, morph), value: zero-filled morph
aligned_morphs = {}

for morpheme, aligned_sym_seq in alignments.items():
    #print("--aligned_sym_seq:", aligned_sym_seq)###
    if morpheme not in aligned_morphs:
        aligned_morphs[morpheme] = collections.OrderedDict()
    if aligned_sym_seq:
        l = len(aligned_sym_seq[0])
        zero_filled_morphs = ["".join([x[i] for x in aligned_sym_seq])
                                for i in range(0,l)]
        original_morphs = [re.sub(r"[Ø ]+", r"", x) for x in zero_filled_morphs]
        for om, zm in zip(original_morphs, zero_filled_morphs):
            if om:
                aligned_morphs[morpheme][om] = zm
    else:
        aligned_morphs[morpheme] = {"": ""}

import pprint
al_fil = open("alignments.py", "w")
pp = pprint.PrettyPrinter(stream = al_fil, width=80)
print("alignments =\\", file = al_fil)
pp.pprint(alignments)
print("\naligned_morphs =\\", file = al_fil)
pp.pprint(aligned_morphs)

# STEP 4:
# Compute the raw morphophonemic representations for each morpheme

morphophon_reprs = {}
for morpheme, dic in aligned_morphs.items():
    #print(morpheme, dic)###
    zero_filled_allomorphs = [dic[allomorph] for allomorph in dic]
    #print("zero_filled_allomorphs:", zero_filled_allomorphs)###
    morphophoneme_list = []
    for i in range(0,len(zero_filled_allomorphs[0])):
        #print(i)###
        phoneme_list = [allomorph[i] for allomorph in zero_filled_allomorphs]
        all_eq = True
        for i in range(0,len(phoneme_list)):
            if phoneme_list[0] != phoneme_list[i]:
                all_eq = False
                break
        if all_eq:
            morphophoneme = phoneme_list[0]
        else:
            morphophoneme = "{" + "".join(phoneme_list) + "}"
        morphophoneme_list.append(morphophoneme)
    #print("morphophoneme_list:", morphophoneme_list)###
    morphophon_reprs[morpheme] = " ".join(morphophoneme_list)
print("morphophon_reprs =\\", file = al_fil)
pp.pprint(morphophon_reprs)

# STEP 5:
# Write the example word forms plus their a zero filled morphs

algfile = open(args.aligned_words, "w", newline='')
writer = csv.DictWriter(algfile,
                        ["MORPHEMES","MORPHS","ALIGNED","MPHONEMIC","PAIRS"],
                        delimiter=args.csv_delimiter)
forms_of_morphs = {}

writer.writeheader()
d = {}
for seg_example in seg_example_list:
    #print("seg_example:", seg_example)###
    morphemes = [morpheme for morpheme, morph in seg_example]
    morphs = [morph for morpheme, morph in seg_example]
    zero_filled_morphs = [aligned_morphs[morpheme].get(morph, "")
                              for (morpheme, morph) in seg_example]
    mphonemes = [morphophon_reprs[morpheme] for morpheme in morphemes]
    d["MORPHEMES"] = " ".join(morphemes)
    d["MORPHS"] = args.morph_separator.join(morphs)
    d["ALIGNED"] = args.morph_separator.join(zero_filled_morphs)
    d["MPHONEMIC"] = " ".join(mphonemes)
    phonemes = list("".join(zero_filled_morphs))
    #print("phonemes:", phonemes)###
    mphonemes = d["MPHONEMIC"].split(" ")
    #print("mphonemes:", mphonemes)###
    mph_ph_list = zip(mphonemes, phonemes)
    pair_list = [p if m==p else m+":"+p for m,p in mph_ph_list]
    #print("pair_list:", pair_list)###
    d["PAIRS"] = " ".join(pair_list)
    writer.writerow(d)
    if morphs[0] not in forms_of_morphs:
        forms_of_morphs[morphs[0]] = set()
    forms_of_morphs[morphs[0]].add(morphemes[1])

algfile.close()

print("forms_of_morphs =\\", file = al_fil)
pp.pprint(forms_of_morphs)


al_fil.close()
