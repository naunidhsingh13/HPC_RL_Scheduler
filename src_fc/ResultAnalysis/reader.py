import pandas as pd

headers = ["id",
           "req_proc_no",
           "req_nodes_no",
           "request_time",
           "run_time",
           "wait_time",
           "submit_time",
           "start_time",
           "finish_time",
           # "some"
           ]

total_nodes = 4360

# df = pd.read_csv("Results_CQSim/theta_data_100.rst", sep=";", header=None)
df = pd.read_csv("theta_data_rl3.rst", sep=";", header=None)

df.columns = headers

df["used_core_hrs"] = df["req_nodes_no"]*df["run_time"]
df["turn_around_time"] = df["finish_time"] - df["submit_time"]

makespan = df["finish_time"].max() - df["submit_time"].min()

max_wait = df["wait_time"].max()

avg_wait = df["wait_time"].mean()

max_turn = df["turn_around_time"].max()

avg_turn = df["turn_around_time"].mean()

avg_util = df["used_core_hrs"].sum()/(makespan*total_nodes)

result = [["Max wait", max_wait],
          ["Avg wait", avg_wait],
          ["Max turn", max_turn],
          ["Avg turn", avg_turn],
          ["Avg Util", avg_util],
          ]

for r in result:
    print(r[0], " : ", r[1])

print("End")