#   Copyright 2010 Clinton Woodward and Steve Dower
# 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

'''A Maximum Set of Gaussians landscape.

This plugin provides the `MSG` landscape. The `MaxSetGaussians` class is a helper
class and is not intended to be used directly.
'''

from esec.landscape.real import Real

from numpy import zeros, random, cos, sin, mat, diag, eye, multiply, exp
from numpy import max as numpy_max

class MaxSetGaussians(object):
    '''Helper class for `MSG`. Initialises covariance, meanvector and optimum
    values needed.
    '''
    def __init__(self, ndims, ngauss, lower, upper, globalvalue, ratio, seed=1):
        # keep a copy of the parameters
        self.ndims = ndims = int(ndims)     # dimensionality
        self.ngauss = ngauss = int(ngauss)  # number of gaussian components
        self.upper = upper                  # upper boundary
        self.lower = lower                  # lower boundary
        self.globalvalue = globalvalue      # the value of the global optimum
        self.ratio = ratio                  # values of local optima ([0,ratio*globalvalue])
        
        # Make namespace for each gaussian component
        self.covmatrix_inv = [None] * ngauss    # inverse convariance matrix
        self.meanvector    = None               # mean of each component
        self.optimumvalue  = zeros(ngauss)      # peak value of each components
        
        # Create a seeded random object for repeatable testing.
        # However - uses the numpy.random module, so seed
        robj = random.RandomState(seed)
        frand = robj.normal
        rand = robj.rand
        
        # Create the rotation matrix
        tmp_eye = mat(eye(ndims))
        rotation = [ tmp_eye.copy() for i in xrange(ngauss) ]
        
        for i in xrange(ngauss):
            for j in xrange(ndims - 1): # need n(n01)/2 rotation matrices
                for k in xrange(j + 1, ndims):
                    rotate = tmp_eye.copy()
                    alpha = frand() # normal range of [0,1)
                    rotate[j, j] = cos(alpha)
                    rotate[j, k] = sin(alpha)
                    rotate[k, j] = -sin(alpha)
                    rotate[k, k] = cos(alpha)
                    rotation[i] = rotation[i] * rotate # matrix dot() multiply
        
        # Create the covarianace matrix
        variancerange = (upper-lower)/20 # this controls the range of variance
        #note: rand makes numpy array, which works right with diag() later.
        variance = rand(ngauss, ndims) * variancerange + 0.5
        # add 0.5 to avoid zero
        
        for i in xrange(ngauss):
            covmatrix = mat(diag(variance[i]))
            # matrix multiply (dot) as rotation & covmatrix are type matrix
            covmatrix = rotation[i].T * covmatrix * rotation[i]
            # store the inverse (of the square) covariance matrix
            self.covmatrix_inv[i]  = covmatrix.I
        
        # Generate a set of random mean vectors within the specified range
        self.meanvector = rand(ngauss, ndims) * (upper-lower) + lower
        
        # Assign optima values for each component to the array
        self.optimumvalue[0] = globalvalue # best first
        # - the others get range [0,globalvalue*ratio]
        self.optimumvalue[1:ngauss] = rand(1, ngauss-1) * globalvalue * ratio
    
    
    def eval(self, x):
        '''Evaluate a single individual.
        '''
        # Note - original matlab code tested an entire set of individuals
        # we just test one at a time
        ngauss = self.ngauss
        ndims = self.ndims
        meanvector = self.meanvector
        covmatrix_inv = self.covmatrix_inv
        optimumvalue = self.optimumvalue
        
        # calculate the values generated by each component
        tmp = zeros(ngauss)
        for i in xrange(ngauss):
            newx = x - meanvector[i]
            y = multiply((newx * covmatrix_inv[i]), newx)
            tmp[i] = y.sum()
        
        fitness = exp(-0.5*tmp/ndims)
        fitness = multiply(fitness, optimumvalue.T)
        #components = fitness.T
        fitnessvalue = numpy_max(fitness)
        return fitnessvalue
    
    
    def info(self):
        '''Return parameters and calculated matrix
        '''
        result = []
        result.append('----------------------------------------------')
        result.append('Dimensions: %d' % self.ndims)
        result.append('Components (Gaussians): %d' % self.ngauss)
        result.append('Range (lower,upper): (%f,%f)' % (self.lower, self.upper))
        result.append('Best (global) value: %f' % self.globalvalue)
        result.append('Best-to-rest ratio: %f' % self.ratio)
        result.append('Covmatrix: ...')
        #result.append(self.covmatrix_inv)
        result.append('Meanvector: ...')
        #result.append(self.meanvector)
        result.append('Optimum values: ' + str(self.optimumvalue))
        result.append('----------------------------------------------')
        return result

class MSG(Real):
    '''Max Set of Gaussians (MSG) landscape generator
    
    As proposed by Gallagher and Yuan \cite{Gallagher2006 }. Able to create a
    wide range of landscape features with a minimal parameter set.  Uses a set
    of mutivariate Gaussian functions create with the following five
    parameters:
    
    - n = ``parameters`` = dimensionality of the landscape
    - m = ``ngauss`` = number of Gaussian components (functions)
    - D(lower, upper) = ``bounds.{lower, upper }`` = lower and upper range for
      components (homogeneous)
    - p = ``gvalue`` = value of the single global optimum peak
    - r = ``ratio`` = ratio of the local optima to the global optimum
    
    See http://www.itee.uq.edu.au/~marcusg/msg.html for descriptions, examples,
    references and source code (matlab). This subclass uses the real_mst.py
    module to do the acualy work. See code there (based on matlab code made
    available by Gallagher).
    
    Qualities: maximisation, multimodal, non-separable, unconstrained,
    normalised (0.0 to 1.0 if gvalue == 1.0)]
    '''
    normalised = True
    lname = 'Max Set of Gaussians (MSG)'
    
    syntax = {
        'ngauss': int,
        'gvalue': float, # global value
        'ratio': float,
    }
    default = {
        'size': { 'min': 2, 'max': 2 },
        'bounds': { 'lower': -5.0, 'upper': 5.0 },
        'ngauss': 3,   # no. guassian peaks
        'gvalue': 1.0, # global optimum peak value
        'ratio': 0.4,  # gap between best peak and other local optima
    }
    strict = { 'size.exact': '*' }
    
    test_key = (
        ('parameters', int),
        ('bounds.lower', float),
        ('bounds.upper', float),
        ('ngauss', int),
        ('gvalue', float),
        ('ratio', float),
        ('invert', bool),
        ('offset', float),
    )
    test_cfg = (
        '2 -5.0 5.0 3 1.0 0.4',
        '2 -5.0 5.0 3 1.0 0.4 - 3.0'
    )
    
    def __init__(self, cfg):
        '''Initialises the MSG landscape.
        '''
        super(MSG, self).__init__(cfg)
        
        # Create the surrogate MSG object
        self._msg = MaxSetGaussians(self.size.exact,
                                    self.cfg.ngauss,
                                    self.cfg.bounds.lower,
                                    self.cfg.bounds.upper,
                                    self.cfg.gvalue,
                                    self.cfg.ratio,
                                    self.cfg.seed)
        # bind eval method
        if self.invert:
            self.eval = self._eval_invert
            self._eval = self._msg.eval
        else:
            self.eval = self._msg.eval  # direct link to surrogate eval
    
    def _eval_invert(self, indiv):
        '''Return an offset invert eval.
        '''
        # Note: this is needed because Landscape.__init__() won't find ._eval()
        # as it hasn't been bound when its looking!!
        return self.offset - self._eval(indiv)
    
    def info(self, level):
        '''Return the basics, and also Max Set Gaussian settings.
        '''
        result = super(MSG, self).info(level)
        if level > 0:
            result.extend(self._msg.info())
        return result

#==============================================================================

# Initialise the default landscape class to MSG. This makes the plugin behave
# as if this were a built-in landscape.
defaults = {
    'landscape': {
        'class': MSG,
    }
}

#==============================================================================
