import time
import pandas as pd

import sys
sys.path.append("./ddsl_load_tester/ddsl_load_tester")

import ddsl_load_tester as load_tester

from tqdm.auto import tqdm
tqdm.pandas()

loop_timer = load_tester.TimerClass()

# Overwrite this function on your own to get the docker replica count
import docker
client = docker.from_env()
def get_docker_replica_count():
    try:
        s = client.services.get("app_name_web")
        return s.attrs['Spec']['Mode']['Replicated']['Replicas']
    except:
        return None
print('Current Replica Count: ', get_docker_replica_count())

def get_replica_count():
    return {'replica':get_docker_replica_count()}



import numpy as np
def get_user_count(mult=1):
    t = np.arange(0,5,1/6)
    sine_min = 8
    sine_max = 12
    user_count1 = ((sine_max - sine_min)/2) * (np.sin(2 * np.pi * t / 5) + 1) + sine_min

    t = np.arange(0,4,1/6)
    sine_min = 1
    sine_max = 19
    user_count2 = ((sine_max - sine_min)/2) * (np.sin(2 * np.pi * t / 5) + 1) + sine_min

    user_count = list(user_count1) + list(user_count2)
    user_count = [int(round(i*mult)) for i in user_count]
    user_count = list(range(1,user_count[0])) + user_count + ([1]*6)
    return user_count

user_sequence = get_user_count(1)
lt = load_tester.DdslLoadTester(hatch_rate=1, temp_stat_max_len=100, base='http://localhost:8089/')
lt.custom_sensing = get_replica_count
lt.change_count(user_sequence[0])
lt.start_capturing()

# This value is best to be kept over 10 seconds.
loop_time_in_secs = load_tester.get_loop_time_in_secs('10s')

loop_timer.tic()

results = None
for i in tqdm(range(len(user_sequence))):
    user_count = user_sequence[i]
    lt.change_count(user_count)
    
    # decrement the loop processing time to have an accurate time for the loop
    sleep_time = loop_time_in_secs - loop_timer.toc()
    if sleep_time > 0:
        time.sleep(sleep_time)
    
    loop_timer.tic()
    
    result = lt.get_all_stats()
    df_result = pd.DataFrame(data=result)
    
    # ANY CONTROL ACTION GOES HERE
    
    if results is None:
        results = df_result
    else:
        results = results.append(df_result)
    
lt.stop_test()

results, filename = lt.prepare_results_from_df(results)

results.head()

# Plot and analyze the results
res = results

# Generate the report
sla_max_95 = 1200
sla_max_avg = 800
sla_max_median = 800

sla_95_count = sum(res['current_response_time_percentile_95'] > sla_max_95)
sla_avg_count = sum(res['current_response_time_average'] > sla_max_avg)
sla_med_count = sum(res['current_response_time_percentile_50'] > sla_max_median)
avg_replica = np.mean(res['custom_replica'])

print("\t Overall Results:")
print("\t=================================")
print("\t 95th percentile Response Time violations:", sla_95_count)
print("\t median Response Time violations:", sla_med_count)
print("\t average Response Time violations:", sla_avg_count)
print("\t average replica count (cost):", avg_replica)


# Plot the results
import matplotlib.pyplot as plt

plt.figure(figsize=(8,18))
plt.subplot(411)
plt.plot(res['elapsed_min'], res['current_min_response_time'], label='current_min_response_time')
plt.plot(res['elapsed_min'], res['current_response_time_percentile_50'], label='median_response_time')
plt.plot(res['elapsed_min'], res['current_response_time_average'], label='avg_response_time')
plt.plot(res['elapsed_min'], res['current_response_time_percentile_95'], label='95th percentile')
plt.plot(res['elapsed_min'], res['current_max_response_time'], label='current_max_response_time')

plt.xlabel('Time (minutes)')
plt.ylabel('Response Time (ms)')
plt.legend()

plt.subplot(412)
plt.plot(res['elapsed_min'], res['user_count'])
plt.xlabel('Time (minutes)')
plt.ylabel('Num of Users')

plt.subplot(413)
plt.plot(res['elapsed_min'], res['total_rps'])
plt.xlabel('Time (minutes)')
plt.ylabel('Throughput (req/s)')

plt.subplot(414)
# plt.plot(res['elapsed_min'], res['fail_ratio'])
# plt.ylabel('Fail Ratio')
plt.plot(res['elapsed_min'], res['custom_replica'])
plt.ylabel('Replica Count')
plt.xlabel('Time (minutes)')


filename = filename.replace('.csv', '')
plt.savefig(filename + '.png', dpi=300)
plt.savefig(filename + '.pdf')
plt.show()

