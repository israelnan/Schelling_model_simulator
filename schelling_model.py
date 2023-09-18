import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class SchellingModel:
    def __init__(self, size=30, threshold=0.5, empty_ratio=0.2, yellow_ratio=0.5,
                 red_ratio=0.5, blue_ratio=0.5):
        self.empty = None
        self.unhappy = None
        self.city = np.zeros((size, size))
        self.empty_ratio = empty_ratio
        self.yellow_ratio = yellow_ratio
        self.red_ratio = red_ratio
        self.blue_ratio = blue_ratio
        self.size = size
        self.threshold = threshold
        self.steps = [0]
        self.segregations = [0]
        self.segregation = 0
        self.setup_town()

    def setup_town(self):
        empty = int(self.empty_ratio * self.size**2)
        people = self.size**2 - empty
        blues = int(people * self.blue_ratio)
        yellow = int(people * self.yellow_ratio)
        red = people - yellow - blues
        city = np.zeros(900)
        city[:yellow] = 1
        city[-blues:] = 2
        for i in range(self.size**2):
            if red == 0:
                break
            if city[i] == 0:
                city[i] = 3
                red -= 1
        np.random.shuffle(city)
        self.calc_seg()
        self.update_unhappy_and_empty()

    def check_local_seg(self, citizen):
        neg = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if 0 <= citizen[0] + i < self.size and 0 <= citizen[1] + j < self.size:
                    if self.city[citizen[0] + i][citizen[1] + j] == 0 \
                            or self.city[citizen[0] + i][j + citizen[1]] == citizen[2]:
                        neg += 1
        return neg == 8

    def calc_seg(self):
        self.segregation = 0
        for i in range(len(self.city)):
            for j in range(len(self.city)):
                if self.city[i][j] == 0:
                    continue
                if self.check_local_seg((i, j, self.city[i][j])):
                    self.segregation += 1

    def update_unhappy_and_empty(self):
        self.unhappy = []
        self.empty = []
        for i in range(self.size):
            for j in range(self.size):
                citizen = (i, j, self.city[i][j])
                if self.city[i][j] == 0:
                    self.empty.append((i, j))
                elif not self.check_happines(citizen):
                    self.unhappy.append(citizen)

    def check_near_neg(self, x, y):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= x + i < self.size and 0 <= y + j < self.size:
                    person = x + i, y + j, self.city[x + i][y + j]
                    if self.city[x + i][y + j] != 0 and not self.check_happines(
                            person) and person not in self.unhappy:
                        self.unhappy.append(person)

    def check_happines(self, citizen):
        different = 0
        same = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if 0 <= citizen[0] + i < self.size and 0 <= citizen[1] + j < self.size:
                    if self.city[citizen[0] + i][citizen[1] + j] != 0:
                        if self.city[citizen[0] + i][citizen[1] + j] == citizen[2]:
                            same += 1
                        else:
                            different += 1

        if same + different == 0 or (same / (same + different)) >= self.threshold:
            return True
        else:
            return False

    def move_person(self, person):
        rand_empty = np.random.randint(0, len(self.empty))
        empty = self.empty[rand_empty]
        if self.check_happines((empty[0], empty[1], person[2])):
            self.city[person[0]][person[1]] = 0
            self.city[empty[0]][empty[1]] = person[2]
            self.calc_seg()
            self.update_unhappy_and_empty()

    def run(self, th, path):
        self.setup_town()
        self.plotBoard(th, path, 'before')
        while len(self.unhappy) != 0:
            rand = np.random.randint(0, len(self.unhappy))
            person = self.unhappy[rand]
            if person in self.unhappy:
                self.move_person(person)
            self.steps.append(self.steps[-1] + 1)
            self.segregations.append(int(self.segregation / int((1 - self.empty_ratio) * self.size**2)))
        plt.plot(self.steps, self.segregations,"*")
        plt.title(f"Segregation at threshold {self.threshold}")
        plt.ylabel("Segregation")
        plt.xlabel("Time")
        plt.show()
        plt.close()
        self.plotBoard(th, path, 'after')

    def plotBoard(self, th, path, s):
        cmap = ListedColormap(['white', 'yellow', 'blue'])
        plt.pcolor(self.city, cmap=cmap, edgecolors='w', linewidths=1)
        plt.savefig(PATH + f"{path}/plots/plot_{th}_{s}.png")
        plt.show()
        plt.close()


PATH = "C:/Users/USER-1/OneDrive - huji.ac.il/Documents/lyx templates/Using Nature Models/"


def change_empty_ratio():
    empty_ratios_arr = np.arange(0.1, 0.6, 0.01)
    final_segregation_arr = []
    runtime_arr = []
    for empty_ratio in empty_ratios_arr:
        model = SchellingModel(yellow_ratio=0.33, blue_ratio=0.33, red_ratio=0.33,
                               empty_ratio=empty_ratio, threshold=0.4)
        model.run(empty_ratio, "f")
        final_segregation_arr.append(model.segregations[-1])
        runtime_arr.append(model.steps[-1])

    plt.plot(empty_ratios_arr, np.array(final_segregation_arr), '*')
    plt.title("Dependency of level of segregation on the number of empty places")
    plt.xlabel("Ratio of empty places")
    plt.ylabel("Level of segregation")
    plt.grid()
    plt.show()
    plt.savefig(PATH + "f/segVSempty.png")
    plt.close()
    plt.plot(empty_ratios_arr, runtime_arr, '*')
    plt.title("Dependency of time to convergence on the number of empty places")
    plt.xlabel("Number of empty places")
    plt.ylabel("Time to convergence (periods)")
    plt.show()
    plt.savefig(PATH + "f/timeVSempty.png")
    plt.close()


def change_threshold():
    thresholds = np.arange(0.2, 0.7, 0.01)
    segregations= []
    periods_list = []
    for threshold in thresholds:
        model = SchellingModel(yellow_ratio=0.33, blue_ratio=0.33,
                               red_ratio=0.33, empty_ratio=0.4, threshold=threshold)
        model.run(threshold, "s")
        segregations.append(model.segregation)
        periods_list.append(model.steps[-1])

    plt.plot(thresholds, segregations, "*")
    plt.title("Dependency of level of segregation on the threshold")
    plt.xlabel("Threshold")
    plt.ylabel("Level of segregation")
    plt.show()
    plt.savefig(PATH + "s/segVSthresh.png")
    plt.close()
    plt.plot(thresholds, periods_list, "*")
    plt.title("Dependency of time to convergence on the threshold")
    plt.xlabel("Threshold")
    plt.ylabel("Time to convergence (periods)")
    plt.show()
    plt.savefig(PATH + "s/timeVSthresh.png")
    plt.close()


def change_population_ratio():
    yellow_units_list = np.arange(0.3, 0.7, 0.01)
    segregation_list = []
    periods_list = []
    for yellow_units in yellow_units_list:
        model = SchellingModel(yellow_ratio=yellow_units / 2, blue_ratio=yellow_units / 2,
                               red_ratio=1 - yellow_units,
                               empty_ratio=0.31)
        model.run(yellow_units, "t")
        segregation_list.append(model.segregation)
        periods_list.append(model.steps[-1])

    plt.plot(yellow_units_list, segregation_list, "*")
    plt.title("Level of segregation with three races")
    plt.xlabel("Proportion of yellow units")
    plt.ylabel("Level of segregation")
    plt.show()
    plt.savefig(PATH + "t/segVSpeop.png")
    plt.close()
    plt.plot(yellow_units_list, periods_list, "*")
    plt.title("Time convergence with three races")
    plt.xlabel("Proportion of yellow units")
    plt.ylabel("Time to convergence (periods)")
    plt.show()
    plt.savefig(PATH + "t/timeVSpeop.png")
    plt.close()


if __name__ == "__main__":
    change_empty_ratio()
    change_threshold()
    change_population_ratio()
