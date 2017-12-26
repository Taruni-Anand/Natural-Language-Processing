from __future__ import division #To avoid integer division
from operator import itemgetter

with open ("berp-POS-training.txt", "r") as f1, open ("cleaned_file.txt","w") as f2:
    f1.seek(0,0)
    line=f1.readline()
    for line in f1:
        f2.write(line[2:].replace("\t","/"))

with open ("cleaned_file.txt", "r") as f:
    l=f.read()
    if l!='\n':
        tr_string=l
tr_list=tr_string.split()
num_words_train= len(tr_list)



train_words = ['']*num_words_train


train_tags = ['']*num_words_train


for i in range(num_words_train):
    temp_list = tr_list[i].split("/")
    train_words[i] = temp_list[0]
    train_tags[i] = temp_list[1]
    i+=1

trans_dict = {}  #dictionary to store tarnsition probabilities


emission_dict = {} #dictionary to store emission probabilities


baseline_dict = {}
#Dictionary with word as key and its most frequent tag as value

for i in range(num_words_train-1):
    nextkey = train_tags[i]
    firstkey = train_tags[i+1]
    trans_dict[nextkey]=trans_dict.get(nextkey,{})
    trans_dict[nextkey][firstkey] = trans_dict[nextkey].get(firstkey,0)
    trans_dict[nextkey][firstkey]+=1

    nextkey = train_words[i]
    firstkey = train_tags[i]
    emission_dict[nextkey]=emission_dict.get(nextkey,{})
    emission_dict[nextkey][firstkey] = emission_dict[nextkey].get(firstkey,0)
    emission_dict[nextkey][firstkey]+=1

trans_dict['.'] = trans_dict.get('.',{})
trans_dict['.'][train_tags[0]] = trans_dict['.'].get(train_tags[0],0)
trans_dict['.'][train_tags[0]]+=1


last_index = num_words_train-1

#Accounting for the last word-tag pair
nextkey = train_words[last_index]
firstkey = train_tags[last_index]
emission_dict[nextkey]=emission_dict.get(nextkey,{})
emission_dict[nextkey][firstkey] = emission_dict[nextkey].get(firstkey,0)
emission_dict[nextkey][firstkey]+=1

#nested dictionary for transition
for key in trans_dict:
    di = trans_dict[key]
    s = sum(di.values())
    for innkey in di:
        di[innkey] /= s
    di = di.items()
    di = sorted(di,key=lambda x: x[0])
    trans_dict[key] = di
#nested dictionary for emission
for key in emission_dict:
    di = emission_dict[key]
    baseline_dict[key] = max(di, key=di.get)
    s = sum(di.values())
    for innkey in di:
        di[innkey] /= s
    di = di.items()
    di = sorted(di,key=lambda x: x[0])
    emission_dict[key] = di



###Testing Phase###

with open ("test.txt", "r") as f1, open ("cleaned_testfile.txt","w") as f2:#removing the nubers
    f1.seek(0,0)
    line=f1.readline()
    for line in f1:
        f2.write(line[2:])

with open ("cleaned_testfile.txt", "r") as f:   #using the clean file
    test_string=f.read()
test_list=test_string.split()
num_words_test= len(test_list)

test_list = test_string.split()
num_words_test = len(test_list)

test_wordlist = ['']*num_words_test             #list of words in test file

viterbi_tags = ['']*num_words_test                 #list of Viterbi tags

baseline_tags = ['']*num_words_test        #list of baseline tags


for i in range(num_words_test):
    temp_list = test_list[i].split("/")
    test_wordlist[i] = temp_list[0]


    baseline_tags[i] = baseline_dict.get(temp_list[0],'')
    #If unknown word - tag = 'NNP'
    if baseline_tags[i]=='':
        baseline_tags[i]='NNP'



    if i==0:    #Accounting for the 1st word in the test document for the Viterbi
        t_probability = trans_dict['.']
    else:
        t_probability = trans_dict[viterbi_tags[i-1]]

    e_probability = emission_dict.get(test_wordlist[i],'')

    #If unknown word  - tag = 'NNP'
    if e_probability=='':
        viterbi_tags[i]='NNP'

    else:
        max_prod_prob = 0
        counter_trans = 0
        counter_emis =0
        prod_prob = 0
        while counter_trans < len(t_probability) and counter_emis < len(e_probability):
            tag_tr = t_probability[counter_trans][0]
            tag_em = e_probability[counter_emis][0]
            if tag_tr < tag_em:
                counter_trans+=1
            elif tag_tr > tag_em:
                counter_emis+=1
            else:
                prod_prob = t_probability[counter_trans][1] * e_probability[counter_emis][1]
                if prod_prob > max_prod_prob:
                    max_prod_prob = prod_prob
                    viterbi_tags[i] = tag_tr
                counter_trans+=1
                counter_emis+=1


    if viterbi_tags[i]=='': #In case there are no matching entries between the transition tags and emission tags, we choose the most frequent emission tag
        viterbi_tags[i] = max(e_probability,key=itemgetter(1))[0]

#output for Viterbi
j=0
list1=[]
with open ("test.txt","r") as f4:
    line=f4.readline()
    for line in f4:
        if line!='\n':
            list1.append(line.replace('\n','\t'))
f4.close()
file = open("muruganandan-tarunianand-assign2-test-output.txt", "w")
for index in range(len(viterbi_tags)):
    file.write(str(list1[index]) + str(viterbi_tags[index]) + "\n")
    if viterbi_tags[index]=='.':
        file.write('\n')
file.close()

#output for the baseline
j=0
list1=[]
with open ("test.txt","r") as f4:
    line=f4.readline()
    for line in f4:
        if line!='\n':
            list1.append(line.replace('\n','\t'))

file = open("muruganandan-tarunianand-assign2-output-baseline.txt", "w")
for index in range(len(baseline_tags)-1):
    file.write(str(list1[index]) + str(baseline_tags[index]) + "\n")
    if viterbi_tags[index]=='.':
        file.write('\n')
file.close()
