import math
import pytest
from kmeans import (
    distance,
    mean,
    kmeans,
    kmeans1,
    separate_into_bins,
    points_in_centroids,
)


class TestKMeansUtilities:
    def test_distance_2d(self):
        assert distance([0, 0], [3, 4]) == 5.0

    def test_distance_1d(self):
        assert distance([0], [5]) == 5.0

    def test_mean_single_point(self):
        assert mean([[1, 2, 3]]) == [1, 2, 3]

    def test_mean_multiple_points(self):
        assert mean([[0, 0], [2, 4]]) == [1, 2]


class TestSeparateIntoBins:
    def test_equal_sized_bins(self):
        data = [0, 1, 2, 10, 11, 12]
        means = separate_into_bins(data, 2)
        # bin 0: [0,1,2] -> mean 1; bin 1: [10,11,12] -> mean 11
        assert means[0] == pytest.approx(1.0)
        assert means[1] == pytest.approx(11.0)

    def test_max_value_goes_to_last_bin(self):
        data = [0, 5, 10]
        means = separate_into_bins(data, 2)
        # bin width = 5 -> [0,5) -> [0]; [5,10] -> [5,10]
        assert means[0] == 0.0
        assert means[1] == pytest.approx(7.5)

    def test_empty_bin_returns_zero(self):
        data = [1, 2, 100]
        means = separate_into_bins(data, 3)
        assert means[1] == 0.0


class TestKMeans1:
    def test_cluster_simple_two_groups(self):
        data = [0, 1, 2, 100, 101, 102]
        labels, centroids = kmeans1(data, 2)
        unique_labels = set(labels)
        assert len(unique_labels) == 2
        # Points 0,1,2 share a label; points 100,101,102 share the other
        group_a = {i for i, l in enumerate(labels) if l == 0}
        group_b = {i for i, l in enumerate(labels) if l == 1}
        assert group_a == {0, 1, 2} or group_a == {3, 4, 5}

    def test_single_cluster_assigns_all_same_label(self):
        data = [1, 5, 10, 20]
        labels, centroids = kmeans1(data, 1)
        assert all(l == 0 for l in labels)

    def test_k_equals_data_length(self):
        data = [1, 2, 3]
        labels, centroids = kmeans1(data, 3)
        assert sorted(labels) == [0, 1, 2]

    def test_points_in_centroids(self):
        data = [1, 2, 3, 100]
        labels = [0, 0, 0, 1]
        centroids = [2.0, 100.0]
        result = points_in_centroids(data, labels, centroids)
        assert result == {0: [1, 2, 3], 1: [100]}


class TestKMeans:
    def test_cluster_simple_two_groups(self):
        data = [[0, 0], [1, 1], [0, 1], [100, 100], [101, 101], [100, 101]]
        labels, centroids = kmeans(data, 2)
        unique_labels = set(labels)
        assert len(unique_labels) == 2
        # Verify centroids are roughly at the two group centers
        centers = sorted([[round(c[0]), round(c[1])] for c in centroids])
        assert centers[0] == [0, 1]
        assert centers[1] == [100, 101]

    def test_k_equals_data_length(self):
        data = [[0, 0], [1, 1], [2, 2]]
        labels, centroids = kmeans(data, 3)
        assert sorted(labels) == [0, 1, 2]
