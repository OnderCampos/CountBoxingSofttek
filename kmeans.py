import random
import math


def distance(point1, point2):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(point1, point2)))


def mean(points):
    return [sum(p[i] for p in points) / len(points) for i in range(len(points[0]))]


def kmeans(data, k, max_iters=100):
    # Randomly initialize centroids
    centroids = random.sample(data, k)

    for _ in range(max_iters):
        # Assign each data point to the nearest centroid
        labels = [
            min(range(k), key=lambda i: distance(point, centroids[i])) for point in data
        ]

        # Update centroids based on mean of points in each cluster
        new_centroids = [
            mean([data[j] for j in range(len(data)) if labels[j] == i])
            for i in range(k)
        ]

        # Check for convergence
        if centroids == new_centroids:
            break

        centroids = new_centroids

    return labels, centroids
def separate_into_bins(data, k):
    # Find the minimum and maximum values of the data
    min_value = min(data)
    max_value = max(data)

    # Calculate the bin width
    bin_width = (max_value - min_value) / k

    # Initialize a list of empty lists to store values for each bin
    separated_values = [[] for _ in range(k)]

    # Assign each data point to the appropriate bin
    for value in data:
        bin_index = int((value - min_value) // bin_width)
        # Ensure the last bin includes the maximum value
        bin_index = min(bin_index, k - 1)
        separated_values[bin_index].append(value)
    means = [sum(bin_values) / len(bin_values) if bin_values else 0 for bin_values in separated_values]

    return means
def kmeans1(data, k, max_iters=200):
    # Randomly initialize centroids
    centroids = separate_into_bins(data, k)
    #centroids = random.sample(data, k)

    for _ in range(max_iters):
        # Assign each data point to the nearest centroid
        labels = [min(range(k), key=lambda i: abs(point - centroids[i])) for point in data]

        # Update centroids based on mean of points in each cluster
        new_centroids = [sum(data[j] for j in range(len(data)) if labels[j] == i) / labels.count(i) for i in range(k)]

        # Check for convergence
        if centroids == new_centroids:
            break

        centroids = new_centroids

    return labels, centroids


# Function to get points associated with each centroid
def points_in_centroids(data, labels, centroids):
    points_by_centroid = {i: [] for i in range(len(centroids))}
    for point, label in zip(data, labels):
        points_by_centroid[label].append(point)
    return points_by_centroid

