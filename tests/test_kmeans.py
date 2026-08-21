import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from kmeans import distance, mean, kmeans, kmeans1, separate_into_bins, points_in_centroids


def test_distance_between_2d_points():
    assert distance([0, 0], [3, 4]) == 5.0


def test_mean_of_points():
    points = [[0, 0], [2, 4], [4, 8]]
    assert mean(points) == [2.0, 4.0]


def test_kmeans_clusters_simple_1d_data():
    data = [1, 2, 3, 10, 11, 12]
    labels, centroids = kmeans([[x] for x in data], 2)
    assert len(set(labels)) == 2
    assert len(centroids) == 2


def test_kmeans1_clusters_1d_data():
    data = [1, 2, 3, 10, 11, 12]
    labels, centroids = kmeans1(data, 2)
    assert len(set(labels)) == 2
    assert len(centroids) == 2


def test_separate_into_bins_basic():
    data = [1, 2, 3, 10, 11, 12]
    means = separate_into_bins(data, 2)
    assert len(means) == 2
    assert means[0] > 0
    assert means[1] > means[0]


def test_points_in_centroids_groups_correctly():
    data = [1, 2, 10, 11]
    labels = [0, 0, 1, 1]
    centroids = [1.5, 10.5]
    grouped = points_in_centroids(data, labels, centroids)
    assert grouped[0] == [1, 2]
    assert grouped[1] == [10, 11]


def test_kmeans_converges_quickly():
    data = [[0], [1], [2], [10], [11], [12]]
    labels, centroids = kmeans(data, 2, max_iters=10)
    # Labels should be stable; each point assigned to nearest centroid
    for idx, point in enumerate(data):
        distances = [distance(point, c) for c in centroids]
        assert distances.index(min(distances)) == labels[idx]
