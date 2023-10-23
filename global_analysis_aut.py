import json
from re import I
import numpy as np
import yaml
import os


task_set = []

class RBS_task:
    def __init__(self, id, P, CPU, E, C, T, D, S, number_of_nodes, number_of_sequences, WCRT):
        self.id = id
        self.priority = P
        self.adj = 0
        self.E = E
        self.ex_times = C
        self.period = T
        self.deadline = D
        self.sequences = S
        self.cpu = CPU
        self.number_of_nodes = number_of_nodes
        self.number_of_sequences = number_of_sequences
        self.nodesWCET = []
        self.nodesET = []
        self.WCRT_analysis = WCRT
        self.RTs_experiment = []
        self.WCRT_experiment = 0
        self.ART_experiment = 0
        self.BCRT_experiment = 0
        self.lastJOB = 0
        self.periodUS = 0
        self.firstRelTime = 0
        self.replicasExecuted = []

def compute_adj_matrix(A, number_of_nodes):

    #define matrix size
    adj_matrix = [[0 for i in range(number_of_nodes)] for i in range(number_of_nodes)]

    for element in A:
        row_ind = element[1] - 1
        col_ind = element[0] - 1
        adj_matrix [row_ind][col_ind] = 1    

    return adj_matrix

def import_taskset(task_to_parse):
    string = "taskset.json"
    f = open(string, "r")
    data = json.load(f)
    
    #Parse tasks from JSON file
    for task in data['taskset']:
        id = task['id']
        E = list(task['E'])
        C = list(task['C'])
        T = int(task['T'])
        D = int(task['T'])
        S = list(task['SEQ'])
        P = task['P']
        CPU = list(task['AFF'])
        WCRT = task['WCRT']

        #transform prio analysis to prio linux
        #P = 99 - P


        #Compute the number of nodes
        number_of_nodes = 0
        for element in E:
            for index in range(2):
                if element[index] > number_of_nodes:
                    number_of_nodes = element[index]

        #Compute the number of sequences
        number_of_sequences = len(S)
        
        #Add task to taskset list
        imported_task = RBS_task(id, P, CPU, E, C, T, D, S, number_of_nodes, number_of_sequences, WCRT)

        #compute period in microseconds
        #imported_task.periodUS = T * time_unit_length

        task_set.append(imported_task)

    f.close()


def generate_yaml():

    with open('taskset1.yaml', 'w') as file:
        tasks_strings = []

        for task in task_set:

            #nodes
            nodes_yaml = []
            for node in range (task.number_of_nodes):
                node_yaml = {"id" : node, "c" : task.ex_times[node], "p" : 0}
                nodes_yaml.append(node_yaml)
            
            #edges
            edges_yaml = []
            for edge in task.E:
                edge_yaml = {"from" : edge[0], "to" : edge[1]}
                edges_yaml.append(edge_yaml)

            #task
            task_yaml_data = {"t" : task.period, "d" : task.deadline, "prio" : task.priority, "vertices" : nodes_yaml, "edges" : edges_yaml}
            tasks_strings.append(task_yaml_data)

        data_yaml = {
            'tasks' : tasks_strings
            }

        yaml.dump(data_yaml, file, sort_keys=False)
        

def main():

    os.system("rm global_WCRT_analysis.txt")

    for task_nr in range(1,2):
        os.system("rm taskset.json")
        os.system("rm taskset1.yaml")
        string = "cp ./tasksets/taskset" + str(task_nr) + ".json taskset.json"
        os.system(string)
        import_taskset(task_nr)
        generate_yaml()
        os.system("./demo 0 taskset1.yaml")
        task_set.clear()

    return


if __name__ == "__main__":
    main()