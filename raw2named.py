import re,  csv

mphon_name = {
    '{ØaØ´a}': '{Ø´a}', # a<>lgâ
    '{ââáâa}': '{âáa}', # alg<â>
    '{Øu´Ø}': '{Ø´u}', # ku<>mppi
    '{pØØØ}': '{pØ}', # kump<p>i
    '{yyuyuyu}': '{yu}', # k<y>eli
    '{eeáeoeo}': '{eáo}', # ky<e>li ku<á>l`á.n
    '{Ø´Ø´ØØ´}': '{Ø´}', # kye<>li kye<´>le
    '{`Ø`ØØlØ}': '{Ø`l}', # kyel<>i kuál<`>á.n
    '{ieáeiii}': '{ieá}', # kyel<i> kye´l<e>
    '{ØØØeØØØ}': '{ØeØ}', # kye´le<e>st
    '{iijj}': '{ij}', # a´lgâ.igui<j>n
    '{aaaaoo}': '{ao}', # <o>olgij <o>lgijd
    '{}': '{}', #
    '{}': '{}', #
    '{}': '{}', #
    '{}': '{}', #
    '{}': '{}', #
    '{}': '{}', #
    }

# [a-zšžŋđõäöáâ`´]

with open("inari-aligned.csv") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        #print(row)###
        raw_pair_str = row["PAIRS"]
        raw_pair_lst = raw_pair_str.split(" ")
        clean_pair_lst = []
        for raw_pair in raw_pair_lst:
            m = re.fullmatch(r"([^:]+):([^:]+)", raw_pair)
            if m:
                mf, sf = m.groups()
                clean_mf = mphon_name.get(mf, mf)
                clean_pair = clean_mf + ":" + sf
            else:
                clean_pair = raw_pair
            clean_pair_lst.append(clean_pair)
        morpheme_lst = row["MORPHEMES"].strip().split(" ")
        morpheme = re.sub(r"\+", r"", morpheme_lst[1])
        clean_pair_lst.append(morpheme + ":Ø")
        clean_pair_str = " ".join(clean_pair_lst)
        print(clean_pair_str)
