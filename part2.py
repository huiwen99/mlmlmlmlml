import pandas as pd
import numpy as np
import sys

class Set:
    def set_training(self, filename):
        f = open(filename, 'r', encoding='utf8')
        lines = f.readlines()

        words = []
        tags = []

        for line in lines:
            if len(line) != 1:
                word, tag = line.split()
                words.append(word)
                tags.append(tag)

        words = np.array(words)
        tags = np.array(tags)
        df = pd.DataFrame({'words': words, 'tags': tags}, columns=['words', 'tags'])
        self.training = df


class HMM:
    def __init__(self, training_dataset=None):
        self.training_set = training_dataset.training
        self.tags = self.training_set.tags.unique()
        self.words = self.training_set.words.unique()

    def set_training_set(self, training_dataset):
        self.training_set = training_dataset.data

    # To estimate the emission parameters
    def count_y_to_x(self, x, y):
        df = self.training_set
        df = df[df['words'] == x]
        df = df[df['tags'] == y]
        count = df.shape[0]
        return count

    def count_y(self, y):
        df = self.training_set
        df = df[df['tags'] == y]
        count = df.shape[0]
        return count

    def emission_params(self, x, y, k=0.5):
        if x == '#UNK#':
            e = k / (self.count_y(y) + k)
        else:
            num = self.count_y_to_x(x, y)
            den = self.count_y(y) + k
            e = num / den
        return e

    def train_emi_params(self):
        x = []
        params = []
        for word in self.words:
            probs = []
            for tag in self.tags:
                e = self.emission_params(word, tag)
                probs.append(e)
            x.append(word)
            params.append(probs)

        probs = []
        for tag in self.tags:
            e = self.emission_params('#UNK#', tag)
            probs.append(e)
        x.append('#UNK#')
        params.append(probs)

        df = pd.DataFrame({'words': x, 'params': params}, columns=['words', 'params'])
        self.emi_params = df

    def set_emi_params(self, df):
        self.emi_params = df

    # Generating the tag
    def generate_tag(self, input_filename, output_filename=None):
        f = open(output_filename, 'w', encoding="utf8")
        input_file = open(input_filename, 'r', encoding="utf8")

        words = [x.strip() for x in input_file.readlines()]

        for i in range(len(words)):
            x = words[i]
            if x == '':
                f.write("\n")
            else:
                if x in self.words:
                    x1 = x
                else:
                    x1 = '#UNK#'
                row = self.emi_params.loc[self.emi_params['words'] == x1]
                probs = row['params'].values[0]
                pos = np.argmax(probs)
                y = self.tags[pos]

                f.write("{} {}\n".format(x, y))

        f.close()

if __name__=="__main__":
    if len(sys.argv) < 3:
        print("Make sure at least python 3.8 is installed")
        print("Run the file in this format")
        print("python part2.py [dataset] [mode]")
        print("dataset can be EN,SG,CN") # sys.argv[1]
        print("mode can be train or predict") # sys.argv[2]

    else:
        dataset = sys.argv[1]
        mode = sys.argv[2]

        d = Set()
        d.set_training('./{}/train'.format(dataset))
        hmm = HMM(d)
        hmm.dataset = dataset
        
        if mode == "train":
            print("Training parameters")
            hmm.train_emi_params()
            hmm.emi_params.to_pickle("./{}/params.pkl".format(dataset))
            print("Parameters is saved to ./{}/params.pkl".format(dataset))

        elif mode == "predict":
            print("Loading parameters")
            try:
                df = pd.read_pickle("./{}/params.pkl".format(dataset))
                hmm.set_emi_params(df)
            except:
                print("Parameters file can't be found, make sure to run in train mode first")

            print("Generating tags")
            hmm.generate_tag(input_filename="./{}/dev.in".format(dataset), output_filename='./{}/dev.p2.out'.format(dataset))
