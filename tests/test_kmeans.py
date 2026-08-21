import math
import pytest
from kmeans import distance, mean, kmeans, separate_into_bins, kmeans1, points_in_centroids


class TestDistance:
    def test_euclidean_distance_2d(self):
        assert distance([0, 0], [3, 4]) == 5.0

    def test_distance_1d(self):
        assert distance([1], [4]) == 3.0

    def test_distance_zero(self):
        assert distance([2, 2], [2, 2]) == 0.0


class TestMean:
    def test_mean_simple(self):
        assert mean([[1, 2], [3, 4], [5, 6]]) == [3.0, 4.0]

    def test_mean_single_point(self):
        assert mean([[7, 8]]) == [7.0, 8.0]


class TestSeparateIntoBins:
    def test_separates_evenly(self):
        data = [0, 1, 2, 3, 4, 5]
        means = separate_into_bins(data, 3)
        # Bins are [0,1], [2,3], [4,5] -> means 0.5, 2.5, 4.5
        assert means == [0.5, 2.5, 4.5]

    def test_max_value_goes_to_last_bin(self):
        data = [0, 5, 10]
        means = separate_into_bins(data, 2)
        # bin_width=5 -> value 5 goes to bin index 1 because 5//5 = 1, then clamped to min(1,1)=1.
        # So bins are [0] and [5,10] -> means 0.0 and 7.5
        assert means == [0.0, 7.5]

    def test_empty_bin_returns_zero(self):
        data = [0, 10]
        means = separate_into_bins(data, 3)
        # bin_width ~ 3.33 -> 0 in bin0, 10 clamped to bin2 -> bin1 empty
        assert means[1] == 0

    def test_zero_range_data_raises_zero_division(self):
        # separate_into_bins cannot handle a zero range because bin_width becomes 0.
        with pytest.raises(ZeroDivisionError):
            separate_into_bins([5, 5, 5], 1)


class TestKmeans1:
    def test_cluster_simple(self):
        data = [1, 2, 3, 10, 11, 12]
        labels, centroids = kmeans1(data, 2)
        assert len(set(labels)) == 2
        assert len(centroids) == 2
        # Points 1,2,3 should share a label, 10,11,12 the other.
        low_label = labels[data.index(1)]
        high_label = labels[data.index(10)]
        assert low_label != high_label
        assert labels == [low_label, low_label, low_label, high_label, high_label, high_label]

    def test_zero_range_data_raises_zero_division(self):
        # kmeans1 delegates initialization to separate_into_bins, which divides by zero
        # when all data points are identical.
        with pytest.raises(ZeroDivisionError):
            kmeans1([5, 5, 5], 2)

    def test_k_equals_data_size(self):
        data = [1, 2, 3]
        labels, centroids = kmeans1(data, 3)
        assert sorted(labels) == [0, 1, 2]


class TestKmeans:
    def test_kmeans_2d_clusters(self):
        data = [[0, 0], [1, 1], [10, 10], [11, 11]]
        labels, centroids = kmeans(data, 2)
        assert len(labels) == 4
        assert len(centroids) == 2
        # First two and last two should cluster separately.
        assert labels[0] == labels[1]
        assert labels[2] == labels[3]
        assert labels[0] != labels[2]


class TestPointsInCentroids:
    def test_groups_by_label(self):
        data = [1, 2, 3, 4]
        labels = [0, 0, 1, 1]
        centroids = [1.5, 3.5]
        result = points_in_centroids(data, labels, centroids)
        assert result == {0: [1, 2], 1: [3, 4]}
