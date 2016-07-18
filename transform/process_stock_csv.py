#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert to a form better suited for training
"""

import argparse
import logging
import pdb

INDEX_OPEN = 0
INDEX_HIGH = 1
INDEX_LOW = 2
INDEX_CLOSE = 3
INDEX_VOL = 4

logger = logging.getLogger("aiwiz")
margin = 0.004 # tradable fluctuation
scan_range = 1

class TrainingData:
    def __init__(self, count):
        self.data_array = []
        self.data_dict = {}
        self.sample_count = count

    def add_raw(self, line):
        str_ar = str.split(line, ",")
        if str_ar[0] in self.data_dict:
            # we assume that if the date exist, the data exists
            return
        self.data_dict[str_ar[0]] = 1

        # validate the data: Date,Open,High,Low,Close,Volume,Adj Close
        if len(str_ar) != 7:
            logger.debug("wrong data: " + line)
            return

        ar = [float(str_ar[1]),float(str_ar[2]),float(str_ar[3]),float(str_ar[4]),float(str_ar[5])]
        if ar[INDEX_HIGH] < ar[INDEX_LOW] or ar[INDEX_OPEN] > ar[INDEX_HIGH] or ar[INDEX_OPEN] < ar[INDEX_LOW] or \
                        ar[INDEX_CLOSE] > ar[INDEX_HIGH] or ar[INDEX_CLOSE] < ar[INDEX_LOW]:
            logger.debug("wrong data: " + line)
            pdb.set_trace()
            return
        self.data_array.append(ar)

    def generate_output(self, ftrain, ftest):
        current = 10 # data is reverse chronologically ordered, leave a few so we can calculate score
        remain = len(self.data_array) - current - self.sample_count
        test_count = int(len(self.data_array) / 10)
        train_count = remain - test_count
        ftrain.write(str(train_count)+',250,hold,sell,buy\n')
        ftest.write(str(test_count)+',250,hold,sell,buy\n')

        while remain > 0:
            vol_sum = 0
            close_sum = 0
            for i in range(0, self.sample_count):
                d = self.data_array[current+i]
                close_sum += d[INDEX_CLOSE]
                vol_sum += d[INDEX_VOL]

            # base = close_sum / remain # use the average as base
            base = self.data_array[current][INDEX_CLOSE]
            vol_base = vol_sum / self.sample_count

            s = ''
            for i in range(0, self.sample_count):
                d = self.data_array[current+i]
                s = s + '{0},{1},{2},{3},{4},'.format(
                    d[INDEX_OPEN]/base,d[INDEX_HIGH]/base,d[INDEX_LOW]/base,d[INDEX_CLOSE]/base,d[INDEX_VOL]/vol_base)

            min_trade = self.data_array[current][INDEX_CLOSE] * (1.0 - margin)
            max_trade = self.data_array[current][INDEX_CLOSE] * (1.0 + margin)
            target = '0\n'
            for i in range(1, scan_range+1):
                close = self.data_array[current - i][INDEX_CLOSE]
                if close < min_trade:
                    target = '1\n'
                    break
                elif close > max_trade:
                    target = '2\n'
                    break

            if current - 10 < test_count:
                fout = ftest
            else:
                fout = ftrain
            fout.write(s)
            fout.write(target)

            current += 1
            remain -=1


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(threadName)s: %(message)s")
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description='stock timeseries pre-process')
    parser.add_argument("-i", "--input", help="Set input file name.")
    parser.add_argument("-o", "--output", help="Set output file name.")
    parser.add_argument("-c", "--count", help="Set number of data entries to combine into one sample")

    args = parser.parse_args()
    logger.debug(args)
    #pdb.set_trace()

    if args.output == None or args.input == None or args.count == None:
        print("argements not specified")
        exit(1)

    fin = open(args.input)
    ftrain = open(args.output+"train", "w+")
    ftest = open(args.output+"test", "w+")
    fin.readline() # skip first line, which is header

    processed = TrainingData(int(args.count))
    for line in fin:
        processed.add_raw(line)

    processed.generate_output(ftrain, ftest)