import pickle
import sys
import unittest
from itertools import product

import numpy as np

from multivar_horner import HornerMultivarPolynomial, MultivarPolynomial
from multivar_horner.global_settings import FLOAT_DTYPE
from tests.test_helpers import rnd_settings_list
from tests.test_settings import DIM_RANGE, DEGREE_RANGE, TEST_RESULTS_PICKLE, NR_TEST_POLYNOMIALS, NR_COEFF_CHANGES, \
    MAX_COEFF_MAGNITUDE, MAX_NUMERICAL_ERROR


def evaluate_numerical_error(dim, max_degree):
    # basic idea: evaluating a polynomial at x = all 1 should give the sum of coefficients
    # -> any deviation is the numerical error
    results = []
    x = np.ones(dim, dtype=FLOAT_DTYPE)
    max_error = 0.0
    ctr_total = 0
    ctr_total_max = NR_TEST_POLYNOMIALS * NR_COEFF_CHANGES

    print(f'evaluating numerical error: dim: {dim}, max. degree: {max_degree} ...')
    for poly_ctr, (coefficients, exponents) in enumerate(rnd_settings_list(NR_TEST_POLYNOMIALS, dim, max_degree,
                                                                           max_abs_coeff=MAX_COEFF_MAGNITUDE,
                                                                           integer_coeffs=False)):
        # debug: validate_input=True
        nr_monomials = exponents.shape[0]
        # find factorisation (expensive)
        poly_horner = HornerMultivarPolynomial(coefficients, exponents, validate_input=True)

        for coeff_ctr in range(NR_COEFF_CHANGES):
            # simply change coefficients of the found factorisation (cheap)
            coefficients = ((np.random.rand(nr_monomials, 1) - 0.5) * (2 * MAX_COEFF_MAGNITUDE))
            coefficients = coefficients.astype(FLOAT_DTYPE)

            # is testing for in_place=True at the same time
            poly_horner.change_coefficients(coefficients, validate_input=True, in_place=True)
            p_x_horner = poly_horner.eval(x)

            poly = MultivarPolynomial(coefficients, exponents)
            p_x = poly.eval(x)

            # in order to compare to a numerically accurate ground truth
            # increase the accuracy:
            # get info of data type supported by hardware: np.finfo(np.longdouble)
            # NOTE: the initial accuracy of the coefficients is the default float 64-bit accuracy
            # one must NOT create random 128-bit coefficients as ground truth
            # this would cause additional numerical error, because the algorithms have only 64-bit accuracy!
            # -> create 64-bit coefficients, then convert them to 128-bit!
            coefficients = np.asarray(coefficients, dtype=np.float128)
            p_x_expected = np.sum(coefficients) # ground truth

            result = (poly, poly_horner, p_x_expected, p_x, p_x_horner)
            results.append(result)
            abs_numerical_error = abs(p_x_horner - p_x_expected)
            max_error = max(max_error, abs_numerical_error)
            sys.stdout.write(f'(poly #{poly_ctr + 1} coeff #{coeff_ctr + 1}, {(ctr_total + 1) / ctr_total_max:.1%})'
                             f' max numerical error: {max_error:.2e}\r')
            sys.stdout.flush()
            if max_error > MAX_NUMERICAL_ERROR:
                # # DEBUG:
                # with open('coefficients.pickle', 'wb') as f:
                #     pickle.dump(coefficients, f)
                # with open('exponents.pickle', 'wb') as f:
                #     pickle.dump(exponents, f)
                raise AssertionError(f'numerical error {max_error:.2e} exceeded limit of {MAX_NUMERICAL_ERROR :.2e} ')
            ctr_total += 1

        sys.stdout.write("\n")  # move the cursor to the next line

    print('\n... done.\n')
    return results


class NumericalTest(unittest.TestCase):

    def test_numerical_stability(self):
        print('\nevaluating the numerical error:')
        results = []
        for dim, max_degree in product(DIM_RANGE, DEGREE_RANGE):
            results += evaluate_numerical_error(dim, max_degree)  # do not append list as entry

        with open(TEST_RESULTS_PICKLE, 'wb') as f:
            print(f'exporting numerical test results in {TEST_RESULTS_PICKLE}')
            pickle.dump(results, f)

        print('done.\n')
