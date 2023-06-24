from computeEngineManager import computeEngineManager
from google.cloud import compute_v1
from google.cloud import monitoring_v3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


cem = computeEngineManager('pruebas-390516', './key.json')

'''all_vms = cem.list_all_instances()
print(type(all_vms))
print(all_vms)
for zone in all_vms:
    print(zone)
    for vm in all_vms[zone]:
        print('\t'+vm.name)
        print(vm.id)'''

dict = cem.get_cpu_use('20/06/23', '23/06/23', 'hours', '7407536914648961278','max')
time_list_x_axis = []
utilization_list_y_axis = []

for key in dict:
    time_list_x_axis.append(key)
    utilization_list_y_axis.append(float(dict[key])*100)

time_list_x_axis.reverse()
utilization_list_y_axis.reverse()

fig = plt.figure()

ax = fig.add_subplot(111)
ax.plot(time_list_x_axis, utilization_list_y_axis, color='lightblue', linewidth=2)
fig.set_size_inches(20.5, 14.5)

plt.xticks(rotation = 90)
plt.show()