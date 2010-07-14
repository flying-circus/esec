'''Provides the `RealSpecies` and `RealIndividual` classes for
real-valued genomes.
'''
from esec.species import Species
from esec.individual import Individual

# Disabled: method could be a function
#pylint: disable=R0201

# Override Individual to provide one that keeps its valid bounds with it
class RealIndividual(Individual):
    '''An `Individual` for real-valued genomes. The valid range of each
    gene is stored with the individual so it may be used during mutation
    operations without being respecified.
    '''
    def __init__(self, genes, parent, bounds=None, statistic=None):
        '''Initialises a new `RealIndividual`. Instances are generally
        created using the initialisation methods provided by `RealSpecies`.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          genes : iterable(float)
            The sequence of genes that make up the new individual.
          
          parent : `RealIndividual` or `Species`
            Either the `RealIndividual` that was used to generate the
            new individual, or an instance of `RealSpecies`.
            
            If an `RealIndividual` is provided, the values for
            `bounds` are taken from that.
          
          bounds : tuple ``(lower bound, upper bound)``
            The lower and upper limits on values that may be included
            in the genome. It is used to allow mutation operations to
            reintroduce values that are missing from the current
            genome and to maintain valid genomes.
          
          statistic : dict [optional]
            A set of statistic values associated with this individual.
            These are accumulated with ``parent.statistic`` and allow
            statistics to accurately represent the population.
        '''
        if bounds:
            self.bounds = bounds
        elif isinstance(parent, RealIndividual):
            self.bounds = parent.bounds
        else:
            self.bounds = None
        
        super(RealIndividual, self).__init__(genes, parent, statistic)
    
    @property
    def genome_string(self):
        '''Returns a string representation of the genes of this individual.
        '''
        return '[' + ', '.join(['%g' % g for g in self.genome]) + ']'
    
    @property
    def phenome_string(self):
        '''Returns a string representation of the phenome of this individual.
        '''
        return '[' + ', '.join(['%.3f' % p for p in self.phenome]) + ']'

class RealSpecies(Species):
    '''Provides individuals with fixed- or variable-length genomes of
    numeric values. Each gene is a double-precision floating-point value
    between the provided ``lowest`` and ``highest`` values (inclusive).
    '''
    
    name = 'real'
    
    def __init__(self, cfg, eval_default):
        super(RealSpecies, self).__init__(cfg, eval_default)
        # Make some names public within the execution context
        self.public_context = {
            'random_real': self.init_random,
            'real_low': self.init_low,
            'real_high': self.init_high,
            'real_toggle': self.init_toggle,
        }
    
    def _init(self, length, shortest, longest, lowest, highest, bounds, template, _gen):
        '''Returns instances of `RealIndividual` initialised using the function in
        `_gen`.
        '''
        if length != None: shortest = longest = length
        assert shortest > 0, "Shortest must be greater than zero"
        assert longest >= shortest, \
            "Value of longest (%d) must be higher or equal to shortest (%d)" % (longest, shortest)
        
        if template: lowest, highest = template.bounds
        lowest, highest = float(lowest), float(highest)
        assert highest > lowest, "Value of highest (%d) must be higher than lowest (%d)" % (highest, lowest)
        
        if bounds:
            assert isinstance(bounds, (tuple, list)), "Bounds must be a tuple or list with two elements"
            assert len(bounds) == 2, "Bounds must be a tuple or list with two elements"
            if lowest < bounds[0]: lowest = float(bounds[0])
            if highest > bounds[1]: highest = float(bounds[1])
        else:
            bounds = (lowest, highest)

        irand = rand.randrange      #pylint: disable=E0602
        while True:
            length = irand(shortest, longest+1)
            genes = [_gen(lowest, highest, i) for i in xrange(length)]
            yield RealIndividual(genes, self, bounds)
    
    def init_random(self, length=None, shortest=10, longest=10, lowest=0.0, highest=1.0, bounds=None, template=None):
        '''Returns instances of `RealIndividual` initialised with random values.
        
        The value of `bounds` (or `lowest` and `highest`) are stored with the
        individual and are used implicitly for mutation operations involving the
        individual.
        
        :Parameters:
          length : int > 0
            The number of genes to include in each individual. If left
            unspecified, a random number between `shortest` and
            `longest` (inclusive) is used to determine the length of
            each individual.
          
          shortest : int > 0
            The smallest number of genes in any individual.
          
          longest : int > `shortest`
            The largest number of genes in any individual.
          
          lowest : float
            The smallest value of any particular gene.
          
          highest : float > `lowest`
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
          
          template : `RealIndividual` [optional]
            If provided, used to determine the values for `lowest`
            and `highest`.
        '''
        frand = rand.random         #pylint: disable=E0602
        return self._init(length, shortest, longest, lowest, highest, bounds, template,
                          lambda low, high, _: frand() * (high - low) + low)
    
    def init_low(self, length=None, shortest=10, longest=10, lowest=0.0, highest=1.0, bounds=None):
        '''Returns instances of `RealIndividual` initialised with `lowest`.
        
        The value of `bounds` (or `lowest` and `highest`) are stored with the
        individual and are used implicitly for mutation operations involving the
        individual.
        
        :Parameters:
          length : int > 0
            The number of genes to include in each individual. If left
            unspecified, a random number between `shortest` and
            `longest` (inclusive) is used to determine the length of
            each individual.
          
          shortest : int > 0
            The smallest number of genes in any individual.
          
          longest : int > `shortest`
            The largest number of genes in any individual.
          
          lowest : float
            The smallest value of any particular gene.
          
          highest : float > 'lowest'
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
        '''
        return self._init(length, shortest, longest, lowest, highest, bounds, None,
                          lambda low, high, _: low)
    
    def init_high(self, length=None, shortest=10, longest=10, lowest=0.0, highest=1.0, bounds=None):
        '''Returns instances of `RealIndividual` initialised with `highest`.
        
        The value of `bounds` (or `lowest` and `highest`) are stored with the
        individual and are used implicitly for mutation operations involving the
        individual.
        
        :Parameters:
          length : int > 0
            The number of genes to include in each individual. If left
            unspecified, a random number between `shortest` and
            `longest` (inclusive) is used to determine the length of
            each individual.
          
          shortest : int > 0
            The smallest number of genes in any individual.
          
          longest : int > `shortest`
            The largest number of genes in any individual.
          
          lowest : float
            The smallest value of any particular gene.
          
          highest : float > 'lowest'
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
        '''
        return self._init(length, shortest, longest, lowest, highest, bounds, None,
                          lambda low, high, _: high)
    
    def init_toggle(self, length=None, shortest=10, longest=10, lowest=0.0, highest=1.0, bounds=None):
        '''Returns instances of `RealIndividual`. Every second individual (from
        the first one returned) is initialised with `highest`; the remainder with
        `lowest`.
        
        The value of `bounds` (or `lowest` and `highest`) are stored with the
        individual and are used implicitly for mutation operations involving the
        individual.
        
        :Parameters:
          length : int > 0
            The number of genes to include in each individual. If left
            unspecified, a random number between `shortest` and
            `longest` (inclusive) is used to determine the length of
            each individual.
          
          shortest : int > 0
            The smallest number of genes in any individual.
          
          longest : int > `shortest`
            The largest number of genes in any individual.
          
          lowest : float
            The smallest value of any particular gene.
          
          highest : float > 'lowest'
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
        '''
        low_gen = self.init_low(length, shortest, longest, lowest, highest, bounds)
        high_gen = self.init_high(length, shortest, longest, lowest, highest, bounds)
        while True:
            yield next(high_gen)
            yield next(low_gen)
    
    def mutate_random(self, src, per_indiv_rate=1.0, per_gene_rate=0.1):
        '''Mutates a group of individuals by replacing genes with random values.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          src : iterable(`RealIndividual`)
            A sequence of individuals. Individuals are taken one at a time
            from this sequence and either returned unaltered or cloned and
            mutated.
          
          per_indiv_rate : |prob|
            The probability of any individual being mutated. If an individual
            is not mutated, it is returned unmodified.
          
          per_gene_rate : |prob|
            The probability of any gene being mutated. If an individual is not
            selected for mutation (under `per_indiv_rate`) then this value is
            unused.
        '''
        frand = rand.random     #pylint: disable=E0602
        
        do_all_gene = (per_gene_rate >= 1.0)
        do_all_indiv = (per_indiv_rate >= 1.0)
        
        def _mutate(indiv, gene):
            '''Returns a potentially mutated gene.'''
            assert isinstance(indiv, RealIndividual), "Want `RealIndividual`, not `%s`" % type(indiv)
            if do_all_gene or frand() < per_gene_rate:
                return frand() * (indiv.bounds[1] - indiv.bounds[0]) + indiv.bounds[0]
            else:
                return gene
        
        for indiv in src:
            if do_all_indiv or frand() < per_indiv_rate:
                yield type(indiv)([_mutate(indiv, g) for g in indiv.genome], indiv, statistic={ 'mutated': 1 })
            else:
                yield indiv
    
    def mutate_delta(self, src, step_size=0.1, per_indiv_rate=1.0, per_gene_rate=0.1, positive_rate=0.5):
        '''Mutates a group of individuals by adding or subtracting `step_size`
        to or from individiual genes.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          src : iterable(`RealIndividual`)
            A sequence of individuals. Individuals are taken one at a time
            from this sequence and either returned unaltered or cloned and
            mutated.
          
          step_size : float
            The amount to adjust mutated genes by.
          
          per_indiv_rate : |prob|
            The probability of any individual being mutated. If an individual
            is not mutated, it is returned unmodified.
          
          per_gene_rate : |prob|
            The probability of any gene being mutated. If an individual is not
            selected for mutation (under `per_indiv_rate`) then this value is
            unused.
          
          positive_rate : |prob|
            The probability of `step_size` being added to the gene value.
            Otherwise, `step_size` is subtracted.
        '''
        frand = rand.random     #pylint: disable=E0602
        
        do_all_gene = (per_gene_rate >= 1.0)
        do_all_indiv = (per_indiv_rate >= 1.0)
        
        def _mutate(indiv, gene, step_size_sum):
            '''Returns a potentially mutated gene.'''
            assert isinstance(indiv, RealIndividual), "Want `RealIndividual`, not `%s`" % type(indiv)
            if do_all_gene or frand() < per_gene_rate:
                step_size_sum[0] += step_size
                new_gene = gene + (step_size if frand() < positive_rate else -step_size)
                return indiv.bounds[0] if new_gene < indiv.bounds[0] else \
                       indiv.bounds[1] if new_gene > indiv.bounds[1] else new_gene
            else:
                return gene
        
        for indiv in src:
            if do_all_indiv or frand() < per_indiv_rate:
                step_size_sum = [0]
                new_genes = [_mutate(indiv, g, step_size_sum) for g in indiv.genome]
                yield type(indiv)(new_genes, indiv, statistic={ 'mutated': 1, 'step_sum': step_size_sum[0] })
            else:
                yield indiv
    
    def mutate_gaussian(self, src, step_size=0.1, sigma=None, per_indiv_rate=1.0, per_gene_rate=0.1):
        '''Mutates a group of individuals by adding or subtracting a random
        value with Gaussian distribution based on `step_size` or `sigma`.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          src : iterable(`RealIndividual`)
            A sequence of individuals. Individuals are taken one at a time
            from this sequence and either returned unaltered or cloned and
            mutated.
          
          step_size : float
            Determines the standard deviation of the distribution used to
            determine the adjustment amount. If `sigma` is provided, this
            value is ignored.
          
          sigma : float
            The standard deviation of the distribution used determine the
            adjust amount. If omitted, the value of `step_size` is used
            to calculate a value for `sigma`.
          
          per_indiv_rate : |prob|
            The probability of any individual being mutated. If an individual
            is not mutated, it is returned unmodified.
          
          per_gene_rate : |prob|
            The probability of any gene being mutated. If an individual is not
            selected for mutation (under `per_indiv_rate`) then this value is
            unused.
        '''
        sigma = sigma or (step_size * 1.253)
        frand = rand.random     #pylint: disable=E0602
        gauss = rand.gauss      #pylint: disable=E0602
        
        do_all_gene = (per_gene_rate >= 1.0)
        do_all_indiv = (per_indiv_rate >= 1.0)
        
        def _mutate(indiv, gene, step_size_sum):
            '''Returns a potentially mutated gene.'''
            assert isinstance(indiv, RealIndividual), "Want `RealIndividual`, not `%s`" % type(indiv)
            if do_all_gene or frand() < per_gene_rate:
                step = gauss(0, sigma)
                step_size_sum[0] += step
                new_gene = gene + step
                return indiv.bounds[0] if new_gene < indiv.bounds[0] else \
                       indiv.bounds[1] if new_gene > indiv.bounds[1] else new_gene
            else:
                return gene
        
        for indiv in src:
            if do_all_indiv or frand() < per_indiv_rate:
                step_size_sum = [0]
                new_genes = [_mutate(indiv, g, step_size_sum) for g in indiv.genome]
                yield type(indiv)(new_genes, indiv, statistic={ 'mutated': 1, 'step_sum': step_size_sum[0] })
            else:
                yield indiv