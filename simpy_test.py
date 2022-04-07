
from collections import defaultdict

import numpy as np
import simpy
from matplotlib import pyplot as plt
from termcolor import colored

from report4 import defaults, support, theoretic

colors = ['cyan', 'green', 'blue', 'yellow', 'red']


class Metric:
    def __init__(self, system_stack_id, value):
        self.system_stack_id = system_stack_id
        self.value = value

    def __add__(self, other):
        return self.value + other.value

    def __repr__(self):
        return '({} - {})'.format(self.system_stack_id, self.value)


class Metrics:
    def __init__(self):
        self.metrics = defaultdict(list)

    def add(self, time, system_stack_id, value):
        self.metrics[time].append(Metric(system_stack_id, value))

    def print(self):
        for key in self.metrics:
            print('{} | {}'.format(key, self.metrics[key]))

    def average(self, time):
        return self.sum(time) / len(self.metrics[time])

    def sum(self, time):
        result = 0

        for m in self.metrics[time]:
            result += m.value

        return result

    def print_avg(self):
        for key in self.metrics:
            print('{} | {}'.format(key, self.average(key)))

    def get_avg(self):
        result = []

        for key in self.metrics:
            result.append(self.average(key))

        return result


class System(object):
    def __init__(self, system_env, num, worker_group):
        self.env = system_env

        self.num = num
        self.state = True
        self.worker_group = worker_group

        self.action = system_env.process(self.run())

    def run(self):
        while True:
            work_duration = support.get_exp(defaults.lamb)
            recover_duration = support.get_exp(defaults.mu)
            # print('--- {} work {}'.format(num,work_duration))
            # print('--- {} recover {}'.format(num, recover_duration))
            self.state = True
            yield self.env.timeout(work_duration)
            if defaults.DEBUG:
                print(colored(
                    'System {} stopped at {}'.format(self.num, self.env.now), colors[self.num]))
            self.state = False
            request = self.worker_group.request()  # Generate a request event
            if defaults.DEBUG:
                print(colored(
                    'System {} requested a worker at {}'.format(self.num, self.env.now), colors[self.num]))
            yield request
            if defaults.DEBUG:
                print(colored(
                    'System {} got a worker at {}'.format(self.num, self.env.now), colors[self.num]))
            yield self.env.timeout(recover_duration)
            if defaults.DEBUG:
                print(colored(
                    'System {} recovered at {}'.format(self.num, self.env.now), colors[self.num]))
            self.worker_group.release(request)
            if defaults.DEBUG:
                print(colored(
                    'System {} released a worker at {}'.format(self.num, self.env.now), colors[self.num]))


class SystemStack(object):
    def __init__(self, system_stack_env, system_stack_id, system_number, schema, workers_number):
        self.env = system_stack_env

        self.system_stack_id = system_stack_id
        self.schema = schema
        self.systems = []
        self.worker_group = simpy.Resource(self.env, capacity=workers_number)

        for number in range(system_number):
            self.systems.append(System(self.env, number, self.worker_group))

        self.env.process(self.monitor())

    def monitor(self):
        while True:
            statuses = []
            for system in self.systems:
                statuses.append(system.state)

            time = int(self.env.now)
            readiness = self.readiness()
            check = self.check()

            if defaults.DEBUG:
                print('time {} statuses {} with result {} and coefficient {}'.format(time, statuses,
                                                                                     check, readiness))

            metrics.add(time, self.system_stack_id, support.bool_to_int(check))
            # metrics.add(time, self.system_stack_id, bool_to_int(readiness))

            yield self.env.timeout(1)

    def check(self):
        result = True

        for part in self.schema:
            if isinstance(part, int):
                result &= self.systems[part].state
            elif isinstance(part, list):
                temp = False

                for subpart in part:
                    if not isinstance(subpart, int):
                        raise ValueError('invalid type in state {}'.format(type(subpart)))
                    temp |= self.systems[subpart].state

                result &= temp
            else:
                raise ValueError('invalid type in state {}'.format(type(part)))

        return result

    def readiness(self):
        result = 0
        check = 0

        for part in self.schema:
            if isinstance(part, int):
                check += 1
                if self.systems[part].state:
                    result += 1
            elif isinstance(part, list):
                for subpart in part:
                    if not isinstance(subpart, int):
                        raise ValueError('invalid type in state {}'.format(type(subpart)))
                    check += 1
                    if self.systems[subpart].state:
                        result += 1
            else:
                raise ValueError('invalid type in state {}'.format(type(part)))

        if check != len(self.systems):
            raise ValueError(
                'mismatched number of systems in schema {} given vs {} in schema'.format(len(self.systems), check))

        return result / len(self.systems)


metrics = Metrics()

for i in range(defaults.default_system_stacks_number):
    env = simpy.Environment()
    ss = SystemStack(
        system_stack_env=env,
        system_stack_id=i,
        system_number=4,
        schema=defaults.default_schema,
        workers_number=defaults.default_workers_number
    )
    env.run(until=defaults.default_modeling_time)

# metrics.print()
# metrics.print_avg()

avg_practical = metrics.get_avg()
theoretical_upper = theoretic.calculate_upper_bound(defaults.default_schema, defaults.lamb, defaults.mu)
theoretical_lower = theoretic.calculate_lower_bound(defaults.default_schema, defaults.lamb, defaults.mu)

print(theoretical_upper)
print(theoretical_lower)
print(avg_practical)

# graphs
x_points = np.arange(1, len(avg_practical) + 1)
fig = plt.figure()
plt.plot(x_points.tolist(), avg_practical, label='Practical')
plt.axhline(y=theoretical_upper, color='r', label='Upper bound')
plt.axhline(y=theoretical_lower, color='g', label='Lower bound')
plt.legend()
plt.title('Расчет')
plt.xlabel("Time")
plt.ylabel("К_г")
plt.grid(True)
plt.show()

