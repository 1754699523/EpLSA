lines_1_3 = []
lines_2 = []
lines_1 = []
lines_3 = []
with open("train.source") as f2:
    lines_1_3 = f2.readlines()
for i in range(len(lines_1_3)):
    lines_1.append(lines_1_3[i].split("\t")[0])
    lines_3.append(lines_1_3[i].split("\t")[1])

with open("train.target")as f:
    lines_2 = f.readlines()

with open("train_3_2.source",'w') as f3:
    for i in range(len(lines_1)):
        f3.write(str(lines_3[i])+str(lines_2[i]))
with open("train_3_2.target",'w') as f4:
    for i in range(len(lines_1)):
        f4.write(str(lines_1[i]))