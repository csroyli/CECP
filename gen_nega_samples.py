# encoding: utf-8
# @author: xinhchen
# email: xinhchen2-c@my.cityu.edu.hk

import numpy as np

import argparse

parser = argparse.ArgumentParser(description="postprocess results")
parser.add_argument(
    '-n',
    "--nns",
    default="2",
    help="the number of the generated negative sample of each type",
    type=int,
)
args = parser.parse_args()


def write_a_nega_doc(ofile, doc_num, label, cond_label, doclen, doc_type, line1, emo, cau, emo_list, cau_list, con_list):
    caucnt = 0
    concnt = 0

    new_emo_index = -1
    new_cau_index = []
    lines = []

    for i in range(doclen):
        if i+1 in emo:
            ori_line = emo_list[0].strip().split(",")
            lines.append([str(len(lines)+1)] + ori_line[1:])
            new_emo_index = len(lines)
            if i+1 in cau:
                new_cau_index.append(len(lines))
        elif i+1 in cau:
            ori_line = cau_list[caucnt].strip().split(",")
            lines.append([str(len(lines)+1)] + ori_line[1:])
            new_cau_index.append(len(lines))
            caucnt += 1
        else:
            if concnt < len(con_list):
                ori_line = con_list[concnt].strip().split(",")
                if label == 1 and doc_type == 1 and int(ori_line[1]) == 3:
                    lines.append([str(len(lines)+1)] + ori_line[1:])
                else:
                    lines.append([str(len(lines)+1), '0'] + ori_line[2:])
                concnt += 1

    ofile.write("{} {} {} {}\n".format(doc_num, len(lines), label, cond_label))
    ofile.write('({}, {})'.format(new_emo_index, new_cau_index[0]))
    for i in range(1, len(new_cau_index)):
        ofile.write(', ({}, {})'.format(new_emo_index, new_cau_index[i]))
    ofile.write('\n')
    for i in range(len(lines)):
        ofile.write(','.join(lines[i]) + "\n")


data = open("data_final.txt", 'r', encoding='utf-8').readlines()
ofile = open("data_wneg.txt", 'w', encoding='utf-8')

# if you want to create the dataset with different n, change the following values
n = args.nns

doc_content = {}
doc_id = 0
i = 0
while i < len(data):
    if data[i] == "":
        break
    doclen = int(data[i].split()[1])
    content_list = []
    content_list.append(data[i])
    content_list.append(data[i+1])
    pairs = eval('['+data[i+1].strip()+']')
    emo, cau = zip(*pairs)
    content_list.append(emo)
    content_list.append(cau)
    emo_list = []
    cau_list = []
    con_list = []
    for j in range(doclen):
        if j+1 in emo:
            emo_list.append(data[i+2+j])
            if j+1 in cau:
                cau_list.append(data[i+2+j])
        elif j+1 in cau:
            cau_list.append(data[i+2+j])
        else:
            con_list.append(data[i+2+j])

    content_list.append(emo_list)
    content_list.append(cau_list)
    content_list.append(con_list)

    doc_content[doc_id] = content_list
    doc_id += 1
    i += doclen + 2

cnt = [0, 0]

doc_num = 1
for doc_id in range(len(doc_content)):
    content_list = doc_content[doc_id]
    [line0, line1, emo, cau, emo_list, cau_list, con_list] = content_list
    emo_clause_type = emo_list[0].split(",")[1]
    emoword = emo_list[0].split(",")[2]
    doclen = int(line0.strip().split()[1])
    doc_type = int(line0.strip().split()[2])
    cond_label = 1 if doc_type < 2 else 0
    mark_nega_index = {}

    # 0 is non-causal
    if doc_type > 0:
        write_a_nega_doc(ofile, doc_num, 1, cond_label, doclen, doc_type, line1, emo, cau, emo_list, cau_list, con_list)
        cnt[1] += 1
    else:
        write_a_nega_doc(ofile, doc_num, 0, cond_label, doclen, doc_type, line1, emo, cau, emo_list, cau_list, con_list)
        cnt[0] += 1
    doc_num += 1
    
    # only generate negative sample for Conditional type and Others type
    if doc_type > 0:
        if doc_type == 1:
            # changing the irrelevant context will not affect the causality
            mark_nega_index = {}
            for _ in range(n - n // 2):
                nega_index = np.random.randint(len(doc_content))
                while nega_index in mark_nega_index:
                    nega_index = np.random.randint(len(doc_content))
                mark_nega_index[nega_index] = 1

                nega_con_list = doc_content[nega_index][6]
                new_con_list = []
                tmp_index = 0
                for i in range(len(con_list)):
                    if int(con_list[i].split(',')[1]) != 3:
                        if tmp_index < len(nega_con_list):
                            tmp_parts = nega_con_list[tmp_index].split(',')
                            # make sure the replaced context clauses will not have the conditional context labels
                            new_con_list.append(','.join([tmp_parts[0], '0']+tmp_parts[2:]))
                            tmp_index += 1
                    else:
                        new_con_list.append(con_list[i])
                write_a_nega_doc(ofile, doc_num, 1, cond_label, doclen, doc_type, line1, emo, cau, emo_list, cau_list, new_con_list)
                doc_num += 1
                cnt[1] += 1

            # changing the conditional context will affect the causality
            mark_nega_index = {}
            for _ in range(n + n // 2):
                nega_index = np.random.randint(len(doc_content))
                while nega_index in mark_nega_index:
                    nega_index = np.random.randint(len(doc_content))
                mark_nega_index[nega_index] = 1

                nega_con_list = doc_content[nega_index][6]
                new_con_list = []
                tmp_index = 0
                for i in range(len(con_list)):
                    if int(con_list[i].split(',')[1]) == 3:
                        if tmp_index < len(nega_con_list):
                            tmp_parts = nega_con_list[tmp_index].split(',')
                            # make sure the replaced context clauses will not have the conditional context labels
                            new_con_list.append(','.join([tmp_parts[0], '0']+tmp_parts[2:]))
                            tmp_index += 1
                    else:
                        new_con_list.append(con_list[i])
                write_a_nega_doc(ofile, doc_num, 0, cond_label, doclen, doc_type, line1, emo, cau, emo_list, cau_list, new_con_list)
                doc_num += 1
                cnt[0] += 1
        else:
            # for other types of document with causal relationship, changing the context will not affect the causality
            mark_nega_index = {}
            for _ in range(n):
                nega_index = np.random.randint(len(doc_content))
                while nega_index in mark_nega_index:
                    nega_index = np.random.randint(len(doc_content))
                mark_nega_index[nega_index] = 1

                nega_con_list = doc_content[nega_index][6]
                write_a_nega_doc(ofile, doc_num, 1, cond_label, doclen, doc_type, line1, emo, cau, emo_list, cau_list, nega_con_list)
                doc_num += 1
                cnt[1] += 1

            # for those emotion and cause being the same clause, we generate more context-type documents
            # since we won't generate emotion-type documents for them
            if len(set(emo) & set(cau)) != 0:
                mark_nega_index = {}
                for _ in range(n):
                    nega_index = np.random.randint(len(doc_content))
                    while nega_index in mark_nega_index:
                        nega_index = np.random.randint(len(doc_content))
                    mark_nega_index[nega_index] = 1

                    nega_con_list = doc_content[nega_index][6]
                    write_a_nega_doc(ofile, doc_num, 1, cond_label, doclen, doc_type, line1, emo, cau, emo_list, cau_list, nega_con_list)
                    doc_num += 1
                    cnt[1] += 1

        # changing the emotion clause will affect the causality
        # to avoid possible confilct, we only generate emotion-type negative samples for those documents with separate e and c
        if len(set(emo) & set(cau)) == 0:
            mark_nega_index = {}
            for _ in range(n):
                nega_index = np.random.randint(len(doc_content))
                negaemoword = doc_content[nega_index][4][0].split(",")[2]
                nega_emoclausetype = doc_content[nega_index][4][0].split(",")[1]
                while nega_index in mark_nega_index or negaemoword == emoword or emo_clause_type != nega_emoclausetype:
                    nega_index = np.random.randint(len(doc_content))
                    negaemoword = doc_content[nega_index][4][0].split(",")[2]
                    nega_emoclausetype = doc_content[nega_index][4][0].split(",")[1]
                mark_nega_index[nega_index] = 1

                nega_emo_list = doc_content[nega_index][4]
                write_a_nega_doc(ofile, doc_num, 0, cond_label, doclen, doc_type, line1, emo, cau, nega_emo_list, cau_list, con_list)
                doc_num += 1
                cnt[0] += 1

print(cnt)