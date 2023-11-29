#%%
# imports
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from enum import Enum
import math
import re

#%%
# constants
EXP_TIME = 2 # duration of the experiment in minutes
N_TARGETS = 10 # targets: numbers 0-9 = 10 targets

# TODO: list correct experiment options
class Experiment(Enum):
    DUMMY = 'dummy'
    MEDIAPIPE = 'Mediapipe_Subsystem'
    VIBROS_LEARNING = 'vibros_learning_curve'
    VIBROS_FINETUNING = 'vibros_finetuning'
    FSR_LEARNING = 'fsr_learning_curve'
    FSR_FINETUNING = 'fsr_finetuning'
    MEDIA_2_VIBROS = 'mediapipe_to_vibros'
    FSR_2_MEDIA = 'fsr_to_mediapipe'

#%%
# variables, TODO: change settings to your needs
# data
experiment = Experiment.MEDIAPIPE.value # possible values specified in enum Experiment (see above)
file_type = ".csv"
data_path = os.path.join("..", "data", experiment)

# column names in the data file
cn_ground_truth = "ground_truth"
cn_response = "response"

# output plot directory
plot_directory = "plots"

# create directory for plots if it does not exist yet
if not os.path.exists(plot_directory):
    os.makedirs(plot_directory)
#%%
# functions
# calculate accuracy
def compute_accuracy(ground_truth, responses):
    n_total = len(ground_truth)
    print("number of targets:", n_total)
    n_correct = np.sum(ground_truth == responses)
    print("number of correct responses:", n_correct)
    accuracy = n_correct / n_total
    print("accuracy:", accuracy)
    return accuracy

# calculate ITR
def compute_itr_bpm(n, p, trials, time):
    if(p==1):
        b = np.log2(n)
    else:
        b = np.log2(n) + p*np.log2(p) + (1-p)*np.log2((1-p)/(n-1))
    information_transfer = b * trials
    itr = information_transfer / time
    return itr

# get the parameters of the experiment
# TODO: adjust name of experiments
def get_parameters(experiment):
    if experiment == Experiment.MEDIAPIPE.value or experiment == Experiment.FSR_FINETUNING.value:
        parameters = np.array([5, 10, 15, 20])
    elif experiment == Experiment.VIBROS_LEARNING.value or experiment == Experiment.FSR_LEARNING.value:
        parameters = np.array(["pre trainig", "session 1", "session 2", "session 3", "session 4", "post training"])
    elif experiment == Experiment.VIBROS_FINETUNING.value:
        parameters = np.array([50, 100, 150, 200])
    elif experiment == Experiment.DUMMY.value:
        parameters = np.array([1,2])
    return parameters

# plot itr
def plot_itr(mean_itrs, parameters, filename, confidence_interval=None, fontsize=14, plot_directory=plot_directory, plot_format=".pdf"):
    fig, ax = plt.subplots()
    x_axis = range(1,len(parameters)+1)
    ax.scatter(x_axis, mean_itrs)
    if confidence_interval is not None:
        ax.errorbar(x_axis, mean_itrs, confidence_interval)
        ax.set_ylim(0, math.ceil(max(mean_itrs)+max(confidence_interval)+5))
    else:
        ax.set_ylim(0, math.ceil(max(mean_itrs)+5))
    ax.set_xticks(x_axis)
    ax.set_xticklabels(parameters, fontsize=fontsize)
    ax.tick_params(axis='both', which='both', direction='in', top=True, right=True, labelsize=fontsize)
    ax.tick_params(axis='x', which='major', pad=10)
    ax.grid(which='major', axis='both', c='lightgray', ls='--')
    ax.set_xlabel("Number of samples", fontsize=fontsize)
    ax.set_ylabel("ITR [bpm]", fontsize=fontsize)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_directory, filename + plot_format))
    return fig


#%%
parameters = get_parameters(experiment)
all_data = []
ids = []
sample_sizes = []

# load data
for file_name in os.listdir(data_path):
    if file_name.endswith(file_type):
        print(file_name)
        file_path = os.path.join(data_path, file_name)
        data = pd.read_csv(file_path, sep=',')
        # Define regular expression patterns to extract numbers
        pattern = r'\d+'
        # Find all matches of the pattern in the string
        matches = re.findall(pattern, file_name)
        # Separate the matches into two lists
        values = [int(match) for match in matches]  # Convert matches to integers
        
        # append lists
        all_data.append(data)
        ids.append(values[0])
        sample_sizes.append(values[1])

num_subs = len(set(ids))
all_itr = np.zeros((num_subs, len(parameters)))

# calculate itrs
for id, sample_size, data in zip(ids, sample_sizes, all_data):
    ground_truth = data[cn_ground_truth].to_numpy()
    responses = data[cn_response].to_numpy()
    
    # compute itr
    trials = len(ground_truth)
    p = compute_accuracy(ground_truth, responses)
    itr = compute_itr_bpm(N_TARGETS, p, trials, EXP_TIME)

    # store itr
    idx_param = np.where(parameters == sample_size)[0][0]
    all_itr[id, idx_param] = itr

# plotting
if num_subs != 0:
    mean_itrs = np.mean(all_itr, axis=0)
    std_err = np.std(all_itr, axis=0) / np.sqrt(num_subs)  # Standard error
    confidence_interval = 1.96 * std_err  # 95% confidence interval
else:
    mean_itrs = all_itr
    confidence_interval = None

plot_name = "ITR_" + experiment
plot = plot_itr(mean_itrs, parameters, plot_name, confidence_interval)
plt.show()