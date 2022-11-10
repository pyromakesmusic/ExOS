import numpy as np

class Config:
    MEAN = [50,50]
    COV = [[10,10],[10,10]]
    TEST_2D_DATA = np.random.multivariate_normal(MEAN, COV, 10000)