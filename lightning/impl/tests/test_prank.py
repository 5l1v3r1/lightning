import numpy as np

from sklearn.datasets import load_diabetes
from sklearn.utils.testing import assert_almost_equal

from lightning.ranking import PRank

bunch = load_diabetes()
X, y = bunch.data, bunch.target
y = np.round(y, decimals=-2)


def test_prank():
    est = PRank(n_iter=10, shuffle=False, random_state=0)
    est.fit(X, y)
    assert_almost_equal(est.score(X, y), 41.86, 2)

    est = PRank(n_iter=10, shuffle=True, random_state=0)
    est.fit(X, y)
    assert_almost_equal(est.score(X, y), 71.04, 2)
