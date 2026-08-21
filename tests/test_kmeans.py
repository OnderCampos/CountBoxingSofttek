import pytest
import math
from kmeans import distance, mean, kmeans, kmeans1, separate_into_bins, points_in_centroids


class TestKmeansUtilities:
    def test_distance_euclidean(self):
        assert distance([0, 0], [3, 4]) == 5.0

    def test_distance_zero(self):
        assert distance([1, 1], [1, 1]) == 0.0

    def test_mean_simple(self):
        assert mean([[0, 0], [2, 4]]) == [1.0, 2.0]

    def test_mean_single_point(self):
        assert mean([[5, 10]]) == [5.0, 10.0]


class TestSeparateIntoBins:
    def test_bins_even_split(self):
        means = separate_into_bins([0, 1, 2, 3, 4, 5], 2)
        # Bins: [0,1,2] mean=1 and [3,4,5] mean=4
        assert means[0] == pytest.approx(1.0)
        assert means[1] == pytest.approx(4.0)

    def test_empty_bin_returns_zero(self):
        means = separate_into_bins([1, 2, 3, 100, 101, 102], 3)
        assert means[1] == 0.0


class TestKmeans1:
    def test_kmeans1_one_cluster(self):
        data = [1, 2, 3, 4, 5]
        labels, centroids = kmeans1(data, 1)
        assert all(label == 0 for label in labels)
        assert len(centroids) == 1

    def test_kmeans1_two_clusters(self):
        data = [1, 2, 3, 100, 101, 102]
        labels, centroids = kmeans1(data, 2)
        assert len(set(labels)) == 2
        assert len(centroids) == 2

    def test_kmeans1_labels_match_centroids_count(self):
        data = [10, 20, 30, 40, 50]
        labels, centroids = kmeans1(data, 2)
        assert len(labels) == len(data)
        assert all(0 <= label < len(centroids) for label in labels)

    def test_points_in_centroids(self):
        data = [1, 2, 100]
        labels = [0, 0, 1]
        centroids = [1.5, 100]
        result = points_in_centroids(data, labels, centroids)
        assert result == {0: [1, 2], 1: [100]}


class TestKmeans2D:
    def test_kmeans_converges(self):
        data = [[0, 0], [0, 1], [10, 10], [10, 11]]
        labels, centroids = kmeans(data, 2, max_iters=100)
        assert len(labels) == len(data)
        assert len(centroids) == 2
        # Points should group by x coordinate
        group_a = {i for i, label in enumerate(labels) if data[i][0] < 5}
        group_b = {i for i, label in enumerate(labels) if data[i][0] > 5}
        assert len(group_a) == 2
        assert len(group_b) == 2
