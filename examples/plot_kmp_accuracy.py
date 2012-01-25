# Author: Mathieu Blondel
# License: BSD
"""
=================================
Kernel Matching Pursuit accuracy
=================================

"""
print __doc__

import sys
import time

import numpy as np
import pylab as pl

from sklearn.linear_model import Ridge

from lightning.datasets import get_loader
from lightning.kmp import KMPClassifier

from sklearn.externals.joblib import Memory
from lightning.datasets import get_data_home

memory = Memory(cachedir=get_data_home(), verbose=0, compress=6)


#@memory.cache
def fit_kmp(X_train, y_train, X_test, y_test):
    start = time.time()
    clf = KMPClassifier(n_nonzero_coefs=30,
                        n_components=0.5,
                        n_refit=0,
                        X_val=X_test, y_val=y_test,
                        metric="rbf", gamma=0.1,
                        n_validate=5,
                        verbose=1,
                        n_jobs=-1)
    clf.fit(X_train, y_train)
    return clf, time.time() - start


try:
    dataset = sys.argv[1]
except:
    dataset = "usps"

try:
    X_train, y_train, X_test, y_test = get_loader(dataset)()
except KeyError:
    raise ValueError("Wrong dataset name!")

clf, time = fit_kmp(X_train, y_train, X_test, y_test)
print "Training done in ", time, " seconds"

pl.figure()
pl.plot(clf.iterations_, clf.scores_)
pl.xlabel('Iteration')
pl.ylabel('Accuracy')
pl.title('Accuracy plot')

pl.show()
