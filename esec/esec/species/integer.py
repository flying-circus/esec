'''Provides the `IntegerSpecies` and `IntegerIndividual` classes for
integer-valued genomes.
'''
from esec.species import Species
from esec.individual import Individual

# Disabled: method could be a function
#pylint: disable=R0201

# Override Individual to provide one that keeps its valid bounds with it
class IntegerIndividual(Individual):
    '''An `Individual` for integer-valued genomes. The valid range of each
    gene is stored with the individual so it may be used during mutation
    operations without being respecified.
    '''
    def __init__(self, genes, parent, bounds=None, statistic=None):
        '''Initialises a new `IntegerIndividual`. Instances are generally
        created using the initialisation methods provided by
        `IntegerSpecies`.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          genes : iterable(int)
            The sequence of genes that make up the new individual.
          
          parent : `IntegerIndividual` or `Species`
            Either the `IntegerIndividual` that was used to generate the
            new individual, or an instance of `IntegerSpecies`.
            
            If an `IntegerIndividual` is provided, the values for
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
        self.bounds = bounds
        
        if isinstance(parent, IntegerIndividual):
            self.bounds = parent.bounds
        
        super(IntegerIndividual, self).__init__(genes, parent, statistic)

class IntegerSpecies(Species):
    '''Provides individuals with fixed- or variable-length genomes of
    integer values. Each gene is an integer between the provided
    ``lowest`` and ``highest`` values (inclusive).
    '''
    
    name = 'integer'
    
    def __init__(self, cfg, eval_default):
        super(IntegerSpecies, self).__init__(cfg, eval_default)
        # Make some names public within the execution context
        self.public_context = {
            'random_int': self.init_random,
            'random_integer': self.init_random,
            'integer_low': self.init_low,
            'integer_high': self.init_high,
            'integer_toggle': self.init_toggle,
            'integer_increment': self.init_increment,
            'integer_count': self.init_count,
        }
    
    def _init(self, length, shortest, longest, lowest, highest, bounds, template, _gen):
        '''Returns instances of `IntegerIndividual` initialised using the function
        in `_gen`.
        '''
        if length != None: shortest = longest = length
        assert shortest > 0, "Shortest must be greater than zero"
        assert longest >= shortest, \
            "Value of longest (%d) must be higher or equal to shortest (%d)" % (longest, shortest)
        
        if template: lowest, highest = template.bounds
        assert type(highest) is type(lowest), "Highest (%s) and lowest (%s) must be the same type." % \
               (type(highest).__name__, type(lowest).__name__)
        assert isinstance(highest, int), "Highest and lowest must be an integer, not %s" % type(highest).__name__
        assert highest > lowest, "Value of highest (%d) must be higher than lowest (%d)" % (highest, lowest)
        
        if bounds:
            assert isinstance(bounds, (tuple, list)), "Bounds must be a tuple or list with two elements"
            assert len(bounds) == 2, "Bounds must be a tuple or list with two elements"
            if lowest < bounds[0]: lowest = int(bounds[0])
            if highest > bounds[1]: highest = int(bounds[1])
        else:
            bounds = (lowest, highest)

        irand = rand.randrange      #pylint: disable=E0602
        while True:
            length = irand(shortest, longest+1)
            genes = [_gen(lowest, highest, i) for i in xrange(length)]
            yield IntegerIndividual(genes, self, bounds)

    def init_random(self, length=None, shortest=10, longest=10, lowest=0, highest=255, bounds=None, template=None):
        '''Returns instances of `IntegerIndividual` initialised with random values.
        
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
          
          lowest : int
            The smallest value of any particular gene.
          
          highest : int > 'lowest'
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
          
          template : `IntegerIndividual` [optional]
            If provided, used to determine the values for `lowest`
            and `highest`.
        '''
        irand = rand.randrange      #pylint: disable=E0602
        return self._init(length, shortest, longest, lowest, highest, bounds, template,
                          lambda low, high, _: irand(low, high + 1))
    
    def init_low(self, length=None, shortest=10, longest=10, lowest=0, highest=255, bounds=None):
        '''Returns instances of `IntegerIndividual` initialised with `lowest`.
        
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
          
          lowest : int
            The smallest value of any particular gene.
          
          highest : int > 'lowest'
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
        '''
        return self._init(length, shortest, longest, lowest, highest, bounds, None,
                          lambda low, high, _: low)
    
    def init_high(self, length=None, shortest=10, longest=10, lowest=0, highest=255, bounds=None):
        '''Returns instances of `IntegerIndividual` initialised with `highest`.
        
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
          
          lowest : int
            The smallest value of any particular gene.
          
          highest : int > 'lowest'
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
        '''
        return self._init(length, shortest, longest, lowest, highest, bounds, None,
                          lambda low, high, _: high)
    
    def init_toggle(self, length=None, shortest=10, longest=10, lowest=0, highest=255, bounds=None):
        '''Returns instances of `IntegerIndividual`. Every second individual (from
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
          
          lowest : int
            The smallest value of any particular gene.
          
          highest : int > 'lowest'
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
    
    def init_increment(self, length=None, shortest=10, longest=10, lowest=0, highest=255, bounds=None):
        '''Returns instances of `IntegerIndividual` initialised with values
        incrementing from `lowest` to `highest` across the genome. If
        `highest` is reached before the end of the genome, counting restarts
        at `lowest`.
        
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
          
          lowest : int
            The smallest value of any particular gene.
          
          highest : int > 'lowest'
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
        '''
        return self._init(length, shortest, longest, lowest, highest, bounds, None,
                          lambda low, high, i: i % (high - low) + low)
    
    def init_count(self, length=None, shortest=10, longest=10, lowest=0, highest=255, bounds=None):
        '''Returns instances of `IntegerIndividual` initialised with each value
        from `lowest` to `highest`. Each genome contains only a single value.
        When `highest` is reached, counting restarts at `lowest`.
        
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
          
          lowest : int
            The smallest value of any particular gene.
          
          highest : int > 'lowest'
            The largest value of any particular gene.
          
          bounds : tuple [optional]
            The hard limits to keep with the individual. If not specified,
            `lowest` and `highest` are assumed to be the limits.
        '''
        low_gen = self.init_low(length, shortest, longest, lowest, highest, bounds)
        while True:
            for i in xrange(lowest, highest + 1):
                indiv = next(low_gen)
                indiv.genome[:] = [i] * len(indiv) #pylint: disable=W0212
                yield indiv
    
    def mutate_random(self, src, per_indiv_rate=1.0, per_gene_rate=0.1):
        '''Mutates a group of individuals by replacing genes with random values.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          src : iterable(`IntegerIndividual`)
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
        irand = rand.randrange  #pylint: disable=E0602
        
        do_all_gene = (per_gene_rate >= 1.0)
        do_all_indiv = (per_indiv_rate >= 1.0)
        
        def _mutate(indiv, gene):
            '''Returns a potentially mutated gene.'''
            assert isinstance(indiv, IntegerIndividual), "Want `IntegerIndividual`, not `%s`" % type(indiv)
            if do_all_gene or frand() < per_gene_rate:
                return irand(*indiv.bounds)
            else:
                return gene
        
        for indiv in src:
            if do_all_indiv or frand() < per_indiv_rate:
                yield type(indiv)([_mutate(indiv, g) for g in indiv.genome], indiv, statistic={ 'mutated': 1 })
            else:
                yield indiv
    
    def mutate_delta(self, src, step_size=1, per_indiv_rate=1.0, per_gene_rate=0.1, positive_rate=0.5):
        '''Mutates a group of individuals by adding or subtracting `step_size`
        to or from individiual genes.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          src : iterable(`IntegerIndividual`)
            A sequence of individuals. Individuals are taken one at a time
            from this sequence and either returned unaltered or cloned and
            mutated.
          
          step_size : int
            The amount to adjust mutated genes by. If this value is not an
            integer, it is truncated before use.
          
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
        
        # Die (if debugging) if step_size is not an integer
        assert step_size == int(step_size), "step_size must be an integer for integer species"
        # Force step_size to be an integer
        step_size = int(step_size)
        
        def _mutate(indiv, gene, step_size_sum):
            '''Returns a potentially mutated gene.'''
            assert isinstance(indiv, IntegerIndividual), "Want `IntegerIndividual`, not `%s`" % type(indiv)
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
    
    def mutate_gaussian(self, src, step_size=1.0, sigma=None, per_indiv_rate=1.0, per_gene_rate=0.1):
        '''Mutates a group of individuals by adding or subtracting a random
        value with Gaussian distribution based on `step_size` or `sigma`.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          src : iterable(`IntegerIndividual`)
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
            assert isinstance(indiv, IntegerIndividual), "Want `IntegerIndividual`, not `%s`" % type(indiv)
            if do_all_gene or frand() < per_gene_rate:
                step = int(gauss(0, sigma))
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