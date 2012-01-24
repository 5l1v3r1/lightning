import numpy as np
import scipy.sparse as sp

from numpy.testing import assert_array_equal, assert_array_almost_equal, \
                          assert_almost_equal
from nose.tools import assert_raises, assert_true, assert_equal

from sklearn.datasets.samples_generator import make_classification
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge

from lightning.kmp import KMPClassifier, KMPRegressor

bin_dense, bin_target = make_classification(n_samples=200, n_features=100,
                                            n_informative=5,
                                            n_classes=2, random_state=0)
bin_sparse = sp.csr_matrix(bin_dense)

mult_dense, mult_target = make_classification(n_samples=300, n_features=100,
                                              n_informative=5,
                                              n_classes=3, random_state=0)
mult_sparse = sp.csr_matrix(mult_dense)


def test_kmp_fit_binary():
    for metric, acc in (("rbf", 0.722),
                        ("linear", 0.90),
                        ("poly", 0.724)):
        kmp = KMPClassifier(n_nonzero_coefs=0.4,
                            dictionary_size=0.5,
                            n_refit=0,
                            metric=metric,
                            random_state=0)
        kmp.fit(bin_dense, bin_target)
        assert_equal(kmp.components_.shape[1], bin_dense.shape[0] / 2)
        y_pred = kmp.predict(bin_dense)
        assert_almost_equal(np.mean(bin_target == y_pred), acc, decimal=2)


def test_kmp_fit_binary_backfitting():
    for metric, acc in (("rbf", 0.5),
                        ("linear", 0.77),
                        ("poly", 0.515)):
        kmp = KMPClassifier(n_nonzero_coefs=0.5,
                            dictionary_size=0.5,
                            n_refit=1,
                            metric=metric,
                            random_state=0)
        kmp.fit(bin_dense, bin_target)
        assert_equal(kmp.components_.shape[1], bin_dense.shape[0] / 2)
        y_pred = kmp.predict(bin_dense)
        assert_almost_equal(np.mean(bin_target == y_pred), acc)


def test_kmp_fit_multiclass():
    for metric, acc in (("rbf", 0.79),
                        ("linear", 0.803),
                        ("poly", 0.846)):
        kmp = KMPClassifier(n_nonzero_coefs=0.4,
                            dictionary_size=0.5,
                            n_refit=10,
                            metric=metric,
                            random_state=0)
        kmp.fit(mult_dense, mult_target)
        y_pred = kmp.predict(mult_dense)
        assert_almost_equal(np.mean(mult_target == y_pred), acc, decimal=2)


def test_kmp_fit_multiclass_check_duplicates():
    for metric, acc in (("rbf", 0.793),
                        ("linear", 0.803),
                        ("poly", 0.846)):
        kmp = KMPClassifier(n_nonzero_coefs=0.4,
                            dictionary_size=0.5,
                            n_refit=10,
                            check_duplicates=True,
                            metric=metric,
                            random_state=0)
        kmp.fit(mult_dense, mult_target)
        y_pred = kmp.predict(mult_dense)
        assert_almost_equal(np.mean(mult_target == y_pred), acc, decimal=2)


def test_kmp_squared_loss():
        kmp = KMPClassifier(n_nonzero_coefs=0.5,
                            dictionary_size=0.5,
                            n_refit=5,
                            estimator=Ridge(alpha=1.0),
                            metric="linear",
                            random_state=0)
        kmp.fit(bin_dense, bin_target)
        y_pred = kmp.decision_function(bin_dense)

        kmp.loss = "squared"
        kmp.fit(bin_dense, bin_target)
        y_pred2 = kmp.decision_function(bin_dense)

        assert_array_almost_equal(y_pred, y_pred2)


def test_kmp_regressor():
    diabetes = load_diabetes()
    X, y = diabetes.data, diabetes.target

    mean, variance = np.mean(y), np.var(y)
    y -= mean
    y /= variance

    reg = KMPRegressor(n_nonzero_coefs=1.0,
                       metric="rbf",
                       gamma=0.1,
                       n_refit=10,
                       estimator=Ridge(alpha=1.0),
                       random_state=0)
    reg.fit(X, y)
    y_pred = reg.predict(X)
    acc = np.sum((y - y_pred) ** 2) / X.shape[0]
    assert_almost_equal(acc, 0.074, decimal=2)
