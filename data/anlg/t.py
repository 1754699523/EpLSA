lines = []
with open("test.target")as f:
    lines = f.readlines()
with open("1.target",'w',encoding='utf-8') as f:
    for i in range(len(lines)):
        f.write(str(lines[i]).split('\t'))
