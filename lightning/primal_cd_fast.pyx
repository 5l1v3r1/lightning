# encoding: utf-8
# cython: cdivision=True
# cython: boundscheck=False
# cython: wraparound=False
#
# Author: Mathieu Blondel
# License: BSD

import numpy as np

cimport numpy as np

cdef extern from "math.h":
   double fabs(double)

cdef extern from "float.h":
   double DBL_MAX

def _primal_cd_l2_svm(weights,
             X,
             np.ndarray[double, ndim=1]y,
             double C,
             int max_iter,
             rs,
             double tol,
             int verbose):

    cdef Py_ssize_t n_samples = X.shape[0]
    cdef Py_ssize_t n_features = X.shape[1]

    cdef np.ndarray[double, ndim=1, mode='c'] w
    w = weights

    cdef int j, s, it, ind = 0
    cdef int active_size = n_features
    cdef int max_num_linesearch = 20

    cdef double sigma = 0.01
    cdef double d, G_loss, G, H
    cdef double Gmax_old = DBL_MAX
    cdef double Gmax_new
    cdef double Gmax_init
    cdef double d_old, d_diff
    cdef double loss_old, loss_new
    cdef double appxcond, cond
    cdef double val, tmp
    cdef double Gp, Gn, violation
    cdef double delta, b_new

    cdef np.ndarray[double, ndim=2, mode='c'] Xnp
    Xnp = X

    cdef np.ndarray[long, ndim=1, mode='c'] index
    index = np.arange(n_features)

    cdef np.ndarray[double, ndim=1, mode='c'] b
    # 1 - y * w^T x
    b = np.ones(n_samples, dtype=np.float64)

    cdef np.ndarray[double, ndim=1, mode='c'] xj_sq
    xj_sq = np.zeros(n_features, dtype=np.float64)

    cdef np.ndarray[double, ndim=1, mode='c'] x_value
    x_value = np.zeros(n_features, dtype=np.float64)

    for j in xrange(n_features):
        for i in xrange(n_samples):
            val = Xnp[i, j]
            # not thread safe !
            Xnp[i, j] *= y[i]
            xj_sq[j] += C * val * val

    for it in xrange(max_iter):
        Gmax_new = 0
        rs.shuffle(index[:active_size])

        s = 0
        while s < active_size:
            j = index[s]
            G_loss = 0
            H = 0

            for ind in xrange(n_samples):
                if b[ind] > 0:
                    val = Xnp[ind, j]
                    tmp = C * val
                    G_loss -= tmp * b[ind]
                    H += tmp * val
            # end for

            G_loss *= 2

            G = G_loss
            H *= 2
            H = max(H, 1e-12)

            Gp = G + 1
            Gn = G - 1
            violation = 0

            if w[j] == 0:
                if Gp < 0:
                    violation = -Gp
                elif Gn > 0:
                    violation = Gn
                elif Gp > Gmax_old / n_samples and Gn < -Gmax_old / n_samples:
                    active_size -= 1
                    index[s], index[active_size] = index[active_size], index[s]
                    continue
            elif w[j] > 0:
                violation = fabs(Gp)
            else:
                violation = fabs(Gn)

            Gmax_new = max(Gmax_new, violation)

            # obtain Newton direction d
            if Gp <= H * w[j]:
                d = -Gp / H
            elif Gn >= H * w[j]:
                d = -Gn / H
            else:
                d = -w[j]

            if fabs(d) < 1.0e-12:
                s += 1
                continue

            delta = fabs(w[j] + d) - fabs(w[j]) + G * d
            d_old = 0

            for num_linesearch in xrange(max_num_linesearch):
                d_diff = d_old - d
                cond = fabs(w[j] + d) - fabs(w[j]) - sigma * delta

                appxcond = xj_sq[j] * d * d + G_loss * d + cond

                if appxcond <= 0:
                    for ind in xrange(n_samples):
                        b[ind] += d_diff * Xnp[ind, j]
                    break

                if num_linesearch == 0:
                    loss_old = 0
                    loss_new = 0

                    for ind in xrange(n_samples):
                        if b[ind] > 0:
                            loss_old += C * b[ind] * b[ind]
                        b_new = b[ind] + d_diff * Xnp[ind, j]
                        b[ind] = b_new

                        if b_new > 0:
                            loss_new += C * b_new * b_new
                else:
                    loss_new = 0

                    for ind in xrange(n_samples):
                        b_new = b[ind] + d_diff * Xnp[ind, j]
                        b[ind] = b_new
                        if b_new > 0:
                            loss_new += C * b_new * b_new

                cond = cond + loss_new - loss_old
                if cond <= 0:
                    break
                else:
                    d_old = d
                    d *= 0.5
                    delta *= 0.5

            # end for num_linesearch

            w[j] += d

            # recompute b[] if line search takes too many steps
            if num_linesearch >= max_num_linesearch:
                b[:] = 1

                for i in xrange(n_features):
                    if w[i] == 0:
                        continue

                    for ind in xrange(n_samples):
                        b[ind] -= w[i] * Xnp[ind, j]
                # end for


            s += 1
        # while active_size

        if it == 0:
            Gmax_init = Gmax_new

        if Gmax_new <= tol * Gmax_init:
            if active_size == n_features:
                if verbose:
                    print "Converged at iteration", it
                break
            else:
                active_size = n_features
                Gmax_old = DBL_MAX
                continue

        Gmax_old = Gmax_new

    # end for while max_iter

    # Restore old values
    for j in xrange(n_features):
        for i in xrange(n_samples):
            Xnp[i, j] *= y[i]

    return w
