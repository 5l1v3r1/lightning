"""
==========================================
Dual Coordinate Descent Solvers
==========================================

This module provides coordinate descent solvers for support vector machines
(SVMs) with L2 regularization.
"""

# Author: Mathieu Blondel
# License: BSD

import numpy as np

from sklearn.base import ClassifierMixin
from sklearn.preprocessing import LabelBinarizer

from .base import BaseClassifier
from .dataset_fast import get_dataset
from .dual_cd_fast import _dual_cd
from .dual_cd_fast import _dual_cd_auc


class LinearSVC(BaseClassifier, ClassifierMixin):
    """Estimator for learning linear support vector machine by coordinate
    descent in the dual.

    Parameters
    ----------
    loss : str, 'hinge', 'squared_hinge'
        The loss function to be used.

    criterion : str, 'accuracy', 'auc'
        Whether to optimize for classification accuracy or AUC.

    C : float
        Weight of the loss term.

    max_iter : int
        Maximum number of iterations to perform.

    tol : float
        Tolerance of the stopping criterion.

    shrinking : bool
        Whether to activate shrinking or not.

    max_steps : int or "auto"
        Maximum number of steps to use during the line search. Use max_steps=0
        to use a constant step size instead of the line search. Use
        max_steps="auto" to let CDClassifier choose the best value.

    warm_start : bool
        Whether to activate warm-start or not.

    permute : bool
        Whether to permute coordinates or not before cycling (only when
        selection='cyclic').

    callback : callable
        Callback function.

    n_calls : int
        Frequency with which `callback` must be called.

    random_state : RandomState or int
        The seed of the pseudo random number generator to use.

    verbose : int
        Verbosity level.

    Example
    -------

    The following example demonstrates how to learn a classification
    model:

    >>> from sklearn.datasets import fetch_20newsgroups_vectorized
    >>> from lightning.dual_cd import LinearSVC
    >>> bunch = fetch_20newsgroups_vectorized(subset="all")
    >>> X, y = bunch.data, bunch.target
    >>> clf = LinearSVC().fit(X, y)
    >>> accuracy = clf.score(X, y)
    """

    def __init__(self, C=1.0, loss="hinge", criterion="accuracy",
                 max_iter=1000, tol=1e-3,
                 permute=True, shrinking=True, warm_start=False,
                 random_state=None, callback=None, n_calls=100, verbose=0):
        self.C = C
        self.loss = loss
        self.criterion = criterion
        self.max_iter = max_iter
        self.tol = tol
        self.permute = permute
        self.shrinking = shrinking
        self.warm_start = warm_start
        self.random_state = random_state
        self.callback = callback
        self.n_calls = n_calls
        self.verbose = verbose
        self.coef_ = None

    def _get_loss(self):
        loss = {"l1": 1,
                "hinge": 1,
                "l2": 2,
                "squared_hinge": 2}
        return loss[self.loss]

    def fit(self, X, y):
        n_samples, n_features = X.shape
        rs = self._get_random_state()

        self.label_binarizer_ = LabelBinarizer(neg_label=-1, pos_label=1)
        Y = np.asfortranarray(self.label_binarizer_.fit_transform(y),
                              dtype=np.float64)
        n_vectors = Y.shape[1]

        ds = get_dataset(X)

        if not self.warm_start or self.coef_ is None:
            self.coef_ = np.zeros((n_vectors, n_features), dtype=np.float64)
            if self.criterion == "accuracy":
                self.dual_coef_ = np.zeros((n_vectors, n_samples),
                                           dtype=np.float64)

        for i in xrange(n_vectors):
            if self.criterion == "accuracy":
                _dual_cd(self, self.coef_[i], self.dual_coef_[i],
                         ds, Y[:, i], self.permute,
                         self.C, self._get_loss(), self.max_iter, rs, self.tol,
                         self.shrinking, self.callback, self.n_calls,
                         verbose=self.verbose)
            else:
                _dual_cd_auc(self, self.coef_[i], ds, Y[:, i],
                             self.C, self._get_loss(), self.max_iter, rs,
                             self.verbose)

        return self
