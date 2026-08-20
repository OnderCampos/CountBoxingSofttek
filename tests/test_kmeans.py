import pytest
import math
from kmeans import distance, mean, kmeans, kmeans1, separate_into_bins, points_in_centroids


class TestDistanceAndMean:
    """Unit tests for low-level math helpers."""

    def test_distance_2d(self):
        assert distance((0, 0), (3, 4)) == pytest.approx(5.0)

    def test_distance_same_point(self):
        assert distance((1, 1), (1, 1)) == 0.0

    def test_distance_3d(self):
        assert distance((0, 0, 0), (1, 2, 2)) == pytest.approx(3.0)

    def test_mean_of_points(self):
        assert mean([(0, 0), (2, 4), (4, 8)]) == [2.0, 4.0]

    def test_mean_single_point(self):
        assert mean([(5, 10)]) == [5.0, 10.0]


class TestSeparateIntoBins:
    """Unit tests for separate_into_bins."""

    def test_separate_into_bins_basic(self):
        data = [0, 1, 2, 3, 4, 5]
        result = separate_into_bins(data, 3)
        # Bins are [0,1], [2,3], [4,5]
        assert result == [pytest.approx(0.5), pytest.approx(2.5), pytest.approx(4.5)]

    def test_separate_into_bins_empty_bin(self):
        data = [0, 5, 10]
        result = separate_into_bins(data, 5)
        # Several bins empty -> mean 0 for those
        assert len(result) == 5
        assert all(isinstance(v, (int, float)) for v in result)

    def test_separate_into_bins_includes_max(self):
        data = [0, 10]
        result = separate_into_bins(data, 2)
        assert result == [pytest.approx(0.0), pytest.approx(10.0)]


class TestKmeans:
    """Unit tests for kmeans clustering."""

    def test_kmeans_converges_on_simple_data(self):
        data = [(0, 0), (0, 1), (10, 10), (10, 11)]
        labels, centroids = kmeans(data, 2, max_iters=100)
        assert len(labels) == len(data)
        assert len(centroids) == 2
        # Each label should be 0 or 1
        assert set(labels) <= {0, 1}

    def test_kmeans_deterministic_when_converged(self):
        data = [(0,), (1,), (10,), (11,)]
        labels, centroids = kmeans(data, 2, max_iters=50)
        # Points 0,1 should share a label; points 10,11 should share the other.
        assert labels[0] == labels[1]
        assert labels[2] == labels[3]
        assert labels[0] != labels[2]


class TestKmeans1:
    """Unit tests for the one-dimensional kmeans1 variant."""

    def test_kmeans1_basic(self):
        data = [0, 1, 2, 10, 11, 12]
        labels, centroids = kmeans1(data, 2, max_iters=100)
        assert len(labels) == len(data)
        assert len(centroids) == 2

    def test_kmeans1_cluster_assignment(self):
        data = [1, 2, 3, 100, 101, 102]
        labels, centroids = kmeans1(data, 2, max_iters=100)
        # Verify low values cluster together and high values cluster together
        low_cluster = labels[0]
        high_cluster = labels[3]
        assert all(labels[i] == low_cluster for i in range(3))
        assert all(labels[i] == high_cluster for i in range(3, 6))
        assert low_cluster != high_cluster


class TestPointsInCentroids:
    """Unit tests for points_in_centroids grouping."""

    def test_points_grouped_by_label(self):
        data = [1, 2, 3, 100]
        labels = [0, 0, 0, 1]
        centroids = [2.0, 100.0]
        grouped = points_in_centroids(data, labels, centroids)
        assert grouped == {0: [1, 2, 3], 1: [100]}
