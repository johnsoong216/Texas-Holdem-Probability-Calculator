import multiprocessing
from joblib import Parallel, delayed
import timeit
import logging

import numpy as np
from collections import Counter

class Ranker:

    @staticmethod
    def rank_all_hands(hand_combos, return_all=False):

        # start = timeit.default_timer()
        rank_res_arr = np.zeros(shape=(hand_combos.shape[1], hand_combos.shape[0]))
        # if hand_combos.shape[0] >= 100000 and hand_combos.shape[1] > 1:
        #     Parallel(n_jobs=multiprocessing.cpu_count(), backend="threading")\
        #              (delayed(Ranker.parallel_rank_hand)(sce, hand_combos, rank_res_arr) for sce in range(hand_combos.shape[1]))
        # else:
        for sce in range(hand_combos.shape[1]):
            Ranker.parallel_rank_hand(sce, hand_combos, rank_res_arr)
        # end = timeit.default_timer()
        # logging.info(f"Ranking all hands time cost: {end - start}")
        if return_all:
            return rank_res_arr
        else:
            return np.max(rank_res_arr, axis=0)

    @staticmethod
    def parallel_rank_hand(scenario, hand_combos, rank_res_arr):
        rank_res_arr[scenario, :] = Ranker.rank_one_hand(hand_combos[:, scenario, :, :])

    @staticmethod
    def rank_one_hand(hand_combos):
        num_combos = hand_combos[:, :, 0]
        num_combos.sort(axis=1)

        suit_combos = hand_combos[:, :, 1]

        suit_arr = gen_suit_arr(suit_combos)
        straight_arr = gen_straight_arr(num_combos)

        rank_arr = np.zeros(num_combos.shape[0], dtype=np.int)

        straight_flush_check(num_combos, rank_arr, straight_arr, suit_arr)
        four_of_a_kind_check(num_combos, rank_arr)
        full_house_check(num_combos, rank_arr)
        flush_check(rank_arr, suit_arr)
        straight_check(num_combos, rank_arr, straight_arr)
        three_of_a_kind_check(num_combos, rank_arr)
        two_pairs_check(num_combos, rank_arr)
        one_pair_check(num_combos, rank_arr)
        return rank_arr * (16 ** 5) + np.sum(num_combos * np.power(16, np.arange(0, 5)), axis=1)


### Helper Functions
def gen_straight_arr(num_combos):
    straight_check = np.zeros(len(num_combos), dtype=np.int)
    for i in range(4):
        if i <= 2:
            straight_check += (num_combos[:, i] == (num_combos[:, i + 1] - 1)).astype(int)
        else:
            straight_check += (num_combos[:, i] == (num_combos[:, i + 1] - 1)).astype(int)
            straight_check += ((num_combos[:, i] == 5) & (num_combos[:, i + 1] == 14)).astype(int)

    return (straight_check == 4)


def gen_suit_arr(suit_combos):
    return np.max(suit_combos, axis=1) == np.min(suit_combos, axis=1)


def straight_flush_check(num_combos, rank_arr, straight_arr, suit_arr):
    rank_arr[(rank_arr == 0) & (straight_arr & suit_arr)] = 8

    # Rearrange order of 2345A to A2345
    reorder_idx = (rank_arr == 8) & (num_combos[:, 0] == 2) & (num_combos[:, 4] == 14)
    num_combos[reorder_idx, :] = np.concatenate([num_combos[reorder_idx, 4:], num_combos[reorder_idx, :4]], axis=1)


def four_of_a_kind_check(num_combos, rank_arr):
    small = np.all(num_combos[:, 0:4] == num_combos[:, :1], axis=1)  # 22223
    large = np.all(num_combos[:, 1:] == num_combos[:, 4:], axis=1)  # 24444

    rank_arr[(rank_arr == 0) & (small | large)] = 7

    reorder_idx = (rank_arr == 7) & small
    num_combos[reorder_idx, :] = np.concatenate([num_combos[reorder_idx, 4:], num_combos[reorder_idx, :4]], axis=1)



def full_house_check(num_combos, rank_arr):
    small = np.all(
        (num_combos[:, 0:3] == num_combos[:, :1])
        & (num_combos[:, 3:4] == num_combos[:, 4:5]), axis=1)  # 22233

    large = np.all(
        (num_combos[:, 0:1] == num_combos[:, 1:2])
        & (num_combos[:, 2:5] == num_combos[:, 4:]), axis=1)  # 22444

    rank_arr[(rank_arr == 0) & (small | large)] = 6

    reorder_idx = (rank_arr == 6) & small
    num_combos[reorder_idx, :] = np.concatenate([num_combos[reorder_idx, 3:], num_combos[reorder_idx, :3]], axis=1)


def flush_check(rank_arr, suit_arr):
    rank_arr[(rank_arr == 0) & suit_arr] = 5


def straight_check(num_combos, rank_arr, straight_arr):
    rank_arr[(rank_arr == 0) & straight_arr] = 4

    # Rearrange order of 2345A to A2345
    reorder_idx = (rank_arr == 4) & (num_combos[:, 0] == 2) & (num_combos[:, 4] == 14)
    num_combos[reorder_idx, :] = np.concatenate([num_combos[reorder_idx, 4:], num_combos[reorder_idx, :4]], axis=1)


def three_of_a_kind_check(num_combos, rank_arr):
    small = np.all(
        (num_combos[:, 0:3] == num_combos[:, :1]), axis=1)  # 22235

    middle = np.all(
        (num_combos[:, 1:4] == num_combos[:, 1:2]), axis=1)  # 23335

    large = np.all(
        (num_combos[:, 2:] == num_combos[:, 2:3]), axis=1)  # 36AAA

    rank_arr[(rank_arr == 0) & (small | middle | large)] = 3

    reorder_small = (rank_arr == 3) & small
    reorder_middle = (rank_arr == 3) & large

    num_combos[reorder_small, :] = np.concatenate([num_combos[reorder_small, 3:], num_combos[reorder_small, :3]],
                                                  axis=1)
    num_combos[reorder_middle, :] = np.concatenate([
        num_combos[reorder_middle, :1],
        num_combos[reorder_middle, 4:],
        num_combos[reorder_middle, 1:4]], axis=1)


def two_pairs_check(num_combos, rank_arr):
    small = np.all(
        (num_combos[:, 0:2] == num_combos[:, :1])
        & (num_combos[:, 2:4] == num_combos[:, 2:3]), axis=1)  # 2233A

    middle = np.all(
        (num_combos[:, 0:2] == num_combos[:, :1])
        & (num_combos[:, 3:] == num_combos[:, 4:]), axis=1)  # 223AA

    large = np.all(
        (num_combos[:, 1:3] == num_combos[:, 1:2])
        & (num_combos[:, 3:] == num_combos[:, 4:]), axis=1)  # 233AA

    rank_arr[(rank_arr == 0) & (small | middle | large)] = 2

    reorder_small = (rank_arr == 2) & small
    reorder_middle = (rank_arr == 2) & large

    num_combos[reorder_small, :] = np.concatenate([num_combos[reorder_small, 4:], num_combos[reorder_small, :4]],
                                                  axis=1)
    num_combos[reorder_middle, :] = np.concatenate([
        num_combos[reorder_middle, 2:3],
        num_combos[reorder_middle, 0:2],
        num_combos[reorder_middle, 3:]], axis=1)


def one_pair_check(num_combos, rank_arr):
    small = np.all(
        (num_combos[:, 0:2] == num_combos[:, :1]), axis=1)  # 22345

    mid_small = np.all(
        (num_combos[:, 1:3] == num_combos[:, 1:2]), axis=1)  # 23345

    mid_large = np.all(
        (num_combos[:, 2:4] == num_combos[:, 2:3]), axis=1)  # 23445

    large = np.all(
        (num_combos[:, 3:] == num_combos[:, 3:4]), axis=1)  # 23455

    rank_arr[(rank_arr == 0) & (small | mid_small | mid_large | large)] = 1

    reorder_small = (rank_arr == 1) & small
    reorder_mid_small = (rank_arr == 1) & mid_small
    reorder_mid_large = (rank_arr == 1) & mid_large

    num_combos[reorder_small, :] = np.concatenate([num_combos[reorder_small, 2:], num_combos[reorder_small, :2]],
                                                  axis=1)
    num_combos[reorder_mid_small, :] = np.concatenate([
        num_combos[reorder_mid_small, :1],
        num_combos[reorder_mid_small, 3:],
        num_combos[reorder_mid_small, 1:3]], axis=1)
    num_combos[reorder_mid_large, :] = np.concatenate([
        num_combos[reorder_mid_large, :2],
        num_combos[reorder_mid_large, 4:],
        num_combos[reorder_mid_large, 2:4]], axis=1)




