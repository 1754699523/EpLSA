with open("test.target",encoding='utf-8') as f:
    t_l = f.readlines()
sum_t = []
print(t_l)
for i in range(len(t_l)):
    t_l[i] = t_l[i].split('\t')
    sum_t.append(t_l[i][0]+'\n')
    sum_t.append(t_l[i][1] + '\n')
    if len(t_l[i])<3:
        sum_t.append(t_l[i][0]+'\n')
    else:
        sum_t.append(t_l[i][2])
with open("test.target",'w',encoding='utf-8') as f:
    f.writelines(sum_t)
# with open("test.source",encoding='utf-8') as f:
#     t_l = f.readlines()
# sum_t = []
# for i in range(len(t_l)):
#     sum_t.append(t_l[i])
#     sum_t.append(t_l[i])
#     sum_t.append(t_l[i])
# with open("test.source",'w',encoding='utf-8') as f:
#     f.writelines(sum_t)