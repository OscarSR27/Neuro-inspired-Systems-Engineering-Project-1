#%%
# imports
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from enum import Enum
import math
import re
import sys

#%%
# constants
EXP_TIME = 2 # duration of the experiment in minutes
N_TARGETS = 10 # targets: numbers 0-9 = 10 targets

# TODO: list correct experiment options
class Experiment(Enum):
    MEDIAPIPE = 'mediapipe_subsystem_parameter_optimization'
    VIBROS_LEARNING = 'vibrotactile_motors_learning_curve'
    VIBROS_FINETUNING = 'vibrotactile_motors_parameter_optimization'
    FSR_LEARNING = 'force_sensor_learning_curve'
    FSR_FINETUNING_SAMPLES = 'force_sensor_sample_size_optimization'
    FSR_FINETUNING_PRESSURE = 'force_sensor_pressure_threshold_optimization'
    MEDIA_2_VIBROS = 'MediaPipe_VTM_ITR'
    FSR_2_MEDIA = 'FS_UDP_ITR'



#%%
# specify variables for data analysis, TODO: change settings to your needs
# data
experiment = Experiment.MEDIAPIPE.value # possible values specified in enum Experiment (see above)
data_path = os.path.join("..", "data", experiment)

# set correct data file extension
if experiment == Experiment.MEDIAPIPE.value:
    file_type = ".csv"
else:
    file_type = ".txt"

# column names in the data file
cn_ground_truth = "ground_truth"
cn_response = "response"

# output directories
plot_directory = "plots"
accuracy_directory = "accuracy_results"
itr_directory = "itr_results"

# create directories if they do not exist yet
for directory in [plot_directory, accuracy_directory, itr_directory]:
    if not os.path.exists(directory):
        os.makedirs(directory)


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
    if experiment == Experiment.MEDIAPIPE.value:
        parameters = np.array([5, 10, 15, 20])
    elif experiment == Experiment.VIBROS_LEARNING.value or experiment == Experiment.FSR_LEARNING.value:
        parameters = np.array(["pre_train", "session1", "session2", "session3", "post_train"])
    elif experiment == Experiment.VIBROS_FINETUNING.value:
        parameters = np.array([250, 500, 750, 1000])
    elif experiment == Experiment.FSR_FINETUNING_SAMPLES.value:
        parameters = np.array([5, 10, 25])
    elif experiment == Experiment.FSR_FINETUNING_PRESSURE.value:
        parameters = np.array([150, 250, 500, 1000])
    else:
        parameters = np.array(["value"])
    return parameters

def save_results(data, column_names, ids, filename):
    df = pd.DataFrame(data=data, columns=column_names, index=ids)
    df.index.name = 'id'
    df.to_csv(filename + '.txt')

def get_xtick_labels(experiment):
    if experiment == Experiment.MEDIAPIPE.value:
        ticklabels = np.array([5, 10, 15, 20])
    elif experiment == Experiment.VIBROS_LEARNING.value or experiment == Experiment.FSR_LEARNING.value:
        ticklabels = np.array(["pre", "training 1", "training 2", "training 3", "post"])
    elif experiment == Experiment.VIBROS_FINETUNING.value:
        ticklabels = np.array([250, 500, 750, 1000])
    elif experiment == Experiment.FSR_FINETUNING_SAMPLES.value:
        ticklabels = np.array([5, 10, 25])
    elif experiment == Experiment.FSR_FINETUNING_PRESSURE.value:
        ticklabels = np.array([150, 250, 500, 1000])
    return ticklabels

def get_xlabel(experiment):
    if experiment == Experiment.MEDIAPIPE.value or experiment == Experiment.FSR_FINETUNING_SAMPLES.value:
        xlabel = "Number of samples"
    elif experiment == Experiment.VIBROS_LEARNING.value or experiment == Experiment.FSR_LEARNING.value:
        xlabel = "Recording session"
    elif experiment == Experiment.VIBROS_FINETUNING.value:
        xlabel = "Stimulation duration [ms]"
    elif experiment == Experiment.FSR_FINETUNING_PRESSURE.value:
        xlabel = "Voltage [$\mu$V]"
    else:
        xlabel = ""
    return xlabel

# plot itr
def plot_itr(itrs, parameters, x_label, filename, # required
             confidence_interval=None, labels = None, # optional params
             fontsize=14, plot_directory=plot_directory, plot_format=".pdf"): # plot params
    fig, ax = plt.subplots()
    x_axis = range(1,len(parameters)+1)
    print(x_axis)
    for i in range(itrs.shape[0]):
        data = itrs[i]
        print(data)
        if labels is not None:
            line, = ax.plot(x_axis, data, marker='o', label=labels[i])
        else:
            line, = ax.plot(x_axis, data, marker='o')
        if confidence_interval is not None:
            line_color = line.get_color()
            ax.errorbar(x_axis, data, confidence_interval[i], c=line_color)
    if confidence_interval is not None:
        ax.set_ylim(0, math.ceil(np.max(itrs)+np.max(confidence_interval)+5))
    else:
        ax.set_ylim(0, math.ceil(np.max(itrs)+5))
    ax.set_xticks(x_axis)
    ax.set_xticklabels(parameters, fontsize=fontsize)
    ax.tick_params(axis='both', which='both', direction='in', top=True, right=True, labelsize=fontsize)
    ax.tick_params(axis='x', which='major', pad=10)
    ax.grid(which='major', axis='both', c='lightgray', ls='--')
    ax.set_xlabel(x_label, fontsize=fontsize)
    ax.set_ylabel("ITR [bpm]", fontsize=fontsize)
    if labels is not None:
        ax.legend(loc='right')
    plt.tight_layout()
    plt.savefig(os.path.join(plot_directory, filename + plot_format))
    return fig


#%%
parameters = get_parameters(experiment)
all_data = []
ids = []
conditions = []

#%% generic code
for i, file_name in enumerate(os.listdir(data_path)):
    if file_name.endswith(file_type):
        print(file_name)
        file_path = os.path.join(data_path, file_name)
        data = pd.read_csv(file_path, sep=',')

        # extract subject id and condition
        if experiment == Experiment.MEDIAPIPE.value or experiment == Experiment.VIBROS_FINETUNING.value or experiment == Experiment.FSR_FINETUNING_SAMPLES.value or experiment == Experiment.FSR_FINETUNING_PRESSURE.value:
            pattern = r'\d+'
            matches = re.findall(pattern, file_name)
            id = int(matches[0])
            cond = int(matches[1])

        elif experiment == Experiment.VIBROS_LEARNING.value or experiment == Experiment.FSR_LEARNING.value:
            pattern = r'subject_id(\d+)_(pre_train|session\d+|post_train)'
            match = re.match(pattern, file_name)
            id = int(match.group(1))
            cond = match.group(2)
        
        elif experiment == Experiment.FSR_2_MEDIA.value or experiment == Experiment.MEDIA_2_VIBROS.value:
            id = i
            cond = "value"

        # append lists
        all_data.append(data)
        ids.append(id)
        conditions.append(cond)


#%%
# calculate the ITR
num_subs = len(set(ids))
all_accuracy = np.zeros((num_subs, len(parameters)))
all_itr = np.zeros((num_subs, len(parameters)))

# calculate itrs
for id, cond, data in zip(ids, conditions, all_data):
    ground_truth = data[cn_ground_truth].to_numpy()
    responses = data[cn_response].to_numpy()
    
    # compute itr
    trials = len(ground_truth)
    p = compute_accuracy(ground_truth, responses)
    itr = compute_itr_bpm(N_TARGETS, p, trials, EXP_TIME)

    # store itr
    idx_param = np.where(parameters == cond)[0][0]
    if experiment == Experiment.FSR_FINETUNING_SAMPLES.value or experiment == Experiment.FSR_FINETUNING_PRESSURE.value:
        all_accuracy[id-1, idx_param] = p
        all_itr[id-1, idx_param] = itr
    else:
        all_accuracy[id, idx_param] = p
        all_itr[id, idx_param] = itr

#%% 
# store results in file
# accuracy
accuracy_file = os.path.join(accuracy_directory, 'ACC_' + experiment)
save_results(all_accuracy, parameters, set(ids), accuracy_file)

# itr
itr_file = os.path.join(itr_directory, 'ITR_' + experiment)
save_results(all_itr, parameters, set(ids), itr_file)

#%%
# no plotting for one-directional communication
if experiment == Experiment.MEDIA_2_VIBROS.value or experiment == Experiment.FSR_2_MEDIA.value:
    sys.exit()

#%%
# plotting
plot_name = "ITR_" + experiment
xlabel = get_xlabel(experiment)
xtick_labels = get_xtick_labels(experiment)

if experiment == Experiment.MEDIAPIPE.value or experiment == Experiment.FSR_LEARNING.value:
    mean_itrs = np.mean(all_itr, axis=0)
    std_err = np.std(all_itr, axis=0) / np.sqrt(num_subs)  # Standard error
    confidence_interval = 1.96 * std_err  # 95% confidence interval
    save_results(np.atleast_2d(mean_itrs), parameters, np.array(['mean']), itr_file+'_mean')
    plot = plot_itr(np.atleast_2d(mean_itrs), xtick_labels, xlabel, plot_name, confidence_interval=np.atleast_2d(confidence_interval))
    plt.show()

elif experiment == Experiment.VIBROS_LEARNING.value:
    plot = plot_itr(all_itr, xtick_labels, xlabel, plot_name, labels=["Simultaneous stimulation", "Sequential stimulation"])
    plt.show()

elif experiment == Experiment.VIBROS_FINETUNING.value or experiment == Experiment.FSR_FINETUNING_SAMPLES.value or experiment == Experiment.FSR_FINETUNING_PRESSURE.value:
    if experiment == Experiment.VIBROS_FINETUNING.value:
        plot_name = plot_name + "_simultaneous"
    plot = plot_itr(all_itr, xtick_labels, xlabel, plot_name)

