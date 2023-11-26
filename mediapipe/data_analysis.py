import os
import numpy as np
import matplotlib.pyplot as plt

# Load python dictionaries for all subjects
data_path = os.path.join("..", "Experiment_data")

all_sample_sizes = []
for filename in os.listdir(data_path):
    if filename.endswith('.npy'):
        file_path = os.path.join(data_path, filename)
        one_subject_one_sample = np.load(file_path, allow_pickle=True)
        all_sample_sizes.append(one_subject_one_sample)

print(all_sample_sizes)

def wrongly_classified(true, signed):
    counts_wrong = 0
    for i in range(len(true)):
        if true[i]!=signed[i]:
            counts_wrong = counts_wrong +1
    return counts_wrong

a=all_sample_sizes[0]
print(a['True numbers'])