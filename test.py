fn1 = "src/eml/all.pkl"
fn2 = "src/json/all.pkl"

# 比较两个文件的差别
import pickle
with open(fn1, "rb") as f:
    data1 = pickle.load(f)
with open(fn2, "rb") as f:
    data2 = pickle.load(f)

print(data1 == data2)
print(data1[0].raw_message)
print(data2)