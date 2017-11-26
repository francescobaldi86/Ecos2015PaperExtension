from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import pairwise_distances
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def clusteringTest(exported, method, nTests, nTestClusters):
    # nTestClusters is a tuple with the range of clusters to be tested. So, for instance, it is (10,20) if a minimum of 10 to a max of 20 clusters are to be tested
    results = np.zeros((nTests,nTestClusters[1]-nTestClusters[0]))
    for idx in range(nTests):
        temp = punctualClustering(exported, method, nTestClusters)
        results[idx][:] = temp
    plt.boxplot(results)
    plt.show()


def punctualClustering(exported, method, nTestClusters):
    storeResults = []
    nAttempts = 10
    X = pd.DataFrame(index=exported.index)
    X["totalElectricDemand"] = exported["totalElectricDemand"]
    X["heatDemandLowTemperature"] = exported["heatDemandLowTemperature"]
    X["heatDemandHighTemperature"] = exported["heatDemandHighTemperature"]
    # Doing the clustering X times for each number of clusters
    clusteringEvaluation = [] # Estimation of the goodness-of-fit for each cluster
    clusterCenters = [] # Storage of the cluster centers
    clusterDuration = [] # Storage of the duration of the time steps for each cluster
    clusterNumber = [] # Storing the number of clusters used
    for nClusters in range(nTestClusters[0], nTestClusters[1]):
        if method=="kmeans":
            [labels, centroids] = kmeansClustering(X, nClusters)
        elif method=="kmedoids":
            [labels, centroids] = kmedoidsClustering(X, nClusters)
        else:
            print("Error in the punctualClustering function: the method given as input should be either kmeans or kmedoids")
        # Adding the centers to the output
        clusterCenters.append(centroids)
        clusterNumber.append(nClusters)
        distanceMatrix = np.zeros((nClusters,len(X.keys())+1))
        clusterDurationVector = np.zeros((nClusters))
        for iCluster in range(nClusters):
            # First, let's count how many clusters of each type there are
            clusterNumber.append(iCluster)
            clusterDurationVector[iCluster] = sum(labels==iCluster) / 4
            data = X[labels == iCluster]
            for iVar in range(len(data.keys())):
                distanceMatrix[iCluster][iVar] = ((data[data.keys()[iVar]] - centroids[iCluster][iVar])**2).sum()**0.5/len(data)
            distanceMatrix[iCluster][len(data.keys())] = data.sub(centroids[iCluster,:]).pow(2).sum(1).pow(0.5).sum()/len(data)/len(X.keys())
        if nClusters == 1:
            clusteringEvaluation.append(distanceMatrix[0][len(data.keys())])
        else:
            clusteringEvaluation.append(np.mean(distanceMatrix[:,len(data.keys())]))
        clusterDuration.append(clusterDurationVector)
    return (clusteringEvaluation, clusterCenters, clusterDuration, clusterNumber)



def kmeansClustering(X, nClusters):
    kmeans = KMeans(n_clusters=nClusters)
    kmeans = kmeans.fit(X)
    labels = kmeans.predict(X)
    centroids = kmeans.cluster_centers_
    return labels, centroids



def kmedoidsClustering(X, nClusters):
    D = pairwise_distances(X, metric='euclidean')
    # split into 2 clusters
    centroids, labels = kMedoids(D, nClusters)
    return labels, centroids



def kMedoids(D, k, tmax=100):
    # determine dimensions of distance matrix D
    m, n = D.shape

    if k > n:
        raise Exception('too many medoids')
    # randomly initialize an array of k medoid indices
    M = np.arange(n)
    np.random.shuffle(M)
    M = np.sort(M[:k])

    # create a copy of the array of medoid indices
    Mnew = np.copy(M)

    # initialize a dictionary to represent clusters
    C = {}
    for t in range(tmax):
        # determine clusters, i. e. arrays of data indices
        J = np.argmin(D[:,M], axis=1)
        for kappa in range(k):
            C[kappa] = np.where(J==kappa)[0]
        # update cluster medoids
        for kappa in range(k):
            J = np.mean(D[np.ix_(C[kappa],C[kappa])],axis=1)
            j = np.argmin(J)
            Mnew[kappa] = C[kappa][j]
        np.sort(Mnew)
        # check for convergence
        if np.array_equal(M, Mnew):
            break
        M = np.copy(Mnew)
    else:
        # final update of cluster memberships
        J = np.argmin(D[:,M], axis=1)
        for kappa in range(k):
            C[kappa] = np.where(J==kappa)[0]

    # return results
    return M, C