"""
============================
Faces dataset decompositions
============================

This example applies to :doc:`/datasets/olivetti_faces` different
unsupervised matrix decomposition (dimension reduction) methods  from the
module :py:mod:`scikits.learn.decomposition` (see the documentation
chapter :ref:`decompositions`) .

"""
print __doc__

# Authors: Vlad Niculae, Alexandre Gramfort
# License: BSD

import logging
from time import time

import pylab as pl

from scikits.learn.datasets import fetch_olivetti_faces
from scikits.learn.cluster import MiniBatchKMeans
from scikits.learn import decomposition

# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
n_row, n_col = 2, 3
n_components = n_row * n_col
image_shape = (64, 64)

###############################################################################
# Load faces data
dataset = fetch_olivetti_faces(shuffle=True)
faces = dataset.data

n_samples, n_features = faces.shape

# global centering
faces_centered = faces - faces.mean(axis=0)

# local centering
faces_centered -= faces_centered.mean(axis=1).reshape(n_samples, -1)

print "Dataset consists of %d faces" % n_samples


###############################################################################
def plot_gallery(title, images):
    pl.figure(figsize=(2. * n_col, 2.26 * n_row))
    pl.suptitle(title, size=16)
    for i, comp in enumerate(images):
        pl.subplot(n_row, n_col, i + 1)
        vmax = max(comp.max(), -comp.min())
        pl.imshow(comp.reshape(image_shape), cmap=pl.cm.gray,
                  interpolation='nearest',
                  vmin=-vmax, vmax=vmax)
        pl.xticks(())
        pl.yticks(())
    pl.subplots_adjust(0.01, 0.05, 0.99, 0.93, 0.04, 0.)

###############################################################################
# List of the different estimators, whether to center and transpose the
# problem, and whether the transformer uses the clustering API.
estimators = [
    ('Eigenfaces - RandomizedPCA',
     decomposition.RandomizedPCA(n_components=n_components, whiten=True),
     True, False),

    ('Non-negative components - NMF',
     decomposition.NMF(n_components=n_components, init='nndsvda', beta=5.0, 
                        tol=5e-3, sparseness='components'),
     False, False),

    ('Independent components - FastICA',
     decomposition.FastICA(n_components=n_components, whiten=True, max_iter=10),
     True, True),

    ('Sparse comp. - MiniBatchSparsePCA',
     decomposition.MiniBatchSparsePCA(n_components=n_components, alpha=1e-3, 
                                      n_iter=100, chunk_size=3),
     True, False),

    ('Cluster centers - MiniBatchKMeans',
     MiniBatchKMeans(k=n_components, tol=1e-3, chunk_size=20, max_iter=50),
     True, False)
]

###############################################################################
# Plot a sample of the input data

plot_gallery("First centered Olivetti faces", faces_centered[:n_components])

###############################################################################
# Do the estimation and plot it

for name, estimator, center, transpose in estimators:
    print "Extracting the top %d %s..." % (n_components, name)
    t0 = time()
    data = faces
    if center:
        data = faces_centered
    if transpose:
        data = data.T
    estimator.fit(data)
    train_time = (time() - t0)
    print "done in %0.3fs" % train_time
    if hasattr(estimator, 'cluster_centers_'):
        components_ = estimator.cluster_centers_
    else:
        components_ = estimator.components_
    if transpose:
        components_ = components_.T
    plot_gallery('%s - Train time %.1fs' % (name, train_time), components_)

pl.show()
