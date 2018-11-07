from numpy import uint32, float64

ID_MULT = False
ID_ADD = True  # ATTENTION: is being used in helpers_fcts_numba.py/eval_recipe()

# numba is expecting certain data types (static typing):
UINT_DTYPE = uint32  # u4 =  4byte unsigned integer
FLOAT_DTYPE = float64  # f8 =  8byte float