'''Provides the `BinarySpecies` class for binary-valued genomes.
'''
from itertools import islice, chain
from esec.species import Species
from esec.individual import Individual
from esec.context import rand
from math import floor
# Disabled: method could be a function
#pylint: disable=R0201

# Override Individual to provide one that provides nicer string formatting.
class BinaryIndividual(Individual):
    '''An `Individual` for binary-valued genomes.
    '''
    
    @property
    def phenome_string(self):
        '''Returns a string representation of the phenome of this individual.
        '''
        return ''.join((str(i) for i in self))

# Override Individual to provide a binary individual with a real-valued phenotype.
class BinaryRealIndividual(Individual):
    '''An `Individual` for binary-valued genomes and real-valued phenomes. Binary
    values are grouped into real-valued parameters, summed and scaled.
    '''
    
    def __init__(self, genes, parent, resolution=0.1, offset=0.0, bits_per_value=None, statistic=None):
        '''Initialises a new individual.
        
        :Parameters:
          genes : iterable
            The sequence of genes that make up the new individual.
          
          parent : `BinaryRealIndividual` or `BinarySpecies`
            Either the `BinaryRealIndividual` that was used to generate
            the new individual, or the `BinarySpecies` descriptor that
            defines the type of individual.
            
            If a `BinaryRealIndividual` is provided, values for
            `resolution`, `offset` and `bits_per_value` are taken from
            this individual.
          
          resolution : float [default 0.1]
            The amount each ``1`` bit contributes to its phenome value.
          
          offset : float [default 0.0]
            The base value, equivalent to all bits zero. Every non-zero
            value is larger than this.
          
          bits_per_value : ``int`` or iterable(``int``)
            The number of bits to use for each phenome value.
          
          statistic : dict [optional]
            A set of statistic values associated with this individual.
            These are accumulated with ``parent.statistic`` and allow
            statistics to accurately represent the population.
        '''
        super(BinaryRealIndividual, self).__init__(genes, parent, statistic)
        
        self._phenome = None
        
        if isinstance(parent, BinaryRealIndividual):
            self.resolution = parent.resolution
            self.bits_per_value = parent.bits_per_value
            self.offset = parent.offset
        else:
            self.resolution = resolution
            self.bits_per_value = int(bits_per_value)
            self.offset = offset
        
        self._format = '%f'
        res = self.resolution
        if res * 10.0 == floor(res * 10.0):
            self._format = '%.1f'
        elif res * 100.0 == floor(res * 100.0):
            self._format = '%.2f'
        elif res * 1000.0 == floor(res * 1000.0):
            self._format = '%.3f'
    
    @property
    def phenome(self):
        '''Returns the phenome of this individual.
        '''
        if not self._phenome:
            _phenome = [ ]
            if hasattr(self.bits_per_value, '__iter__'):
                i = 0
                for bits in self.bits_per_value:
                    if i + bits > len(self.genome): break
                    _phenome.append(sum(self.genome[i:i+bits]))
                    i += bits
            elif self.bits_per_value:
                i = 0
                bits = self.bits_per_value
                while i + bits <= len(self.genome):
                    _phenome.append(sum(self.genome[i:i+bits]))
                    i += bits
            else:
                _phenome.append(sum(self.genome))
            self._phenome = [self.offset + self.resolution * i for i in _phenome]
        return self._phenome
    
    @property
    def phenome_string(self):
        '''Returns a string representation of the phenome of this individual.
        '''
        fmt = self._format
        return '[' + ', '.join(fmt % i for i in self.phenome) + ']'

# Override Individual to provide a binary individual with an integer phenotype.
class BinaryIntegerIndividual(Individual):
    '''An `Individual` for binary-valued genomes and integer phenomes. Binary
    values are grouped into integer parameters, summed and scaled.
    '''
    
    def __init__(self, genes, parent, resolution=1, offset=0, bits_per_value=None, statistic=None):
        '''Initialises a new individual.
        
        :Parameters:
          genes : iterable
            The sequence of genes that make up the new individual.
          
          parent : `BinaryIntegerIndividual` or `BinarySpecies`
            Either the `BinaryIntegerIndividual` that was used to generate
            the new individual, or the `BinarySpecies` descriptor that
            defines the type of individual.
            
            If a `BinaryIntegerIndividual` is provided, values for
            `resolution`, `offset` and `bits_per_value` are taken from
            this individual.
          
          resolution : int [default 1]
            The amount each ``1`` bit contributes to its phenome value.
          
          offset : int [default 0]
            The base value, equivalent to all bits zero. Every non-zero
            value is larger than this.
          
          bits_per_value : ``int`` or iterable(``int``)
            The number of bits to use for each phenome value.
          
          statistic : dict [optional]
            A set of statistic values associated with this individual.
            These are accumulated with ``parent.statistic`` and allow
            statistics to accurately represent the population.
        '''
        super(BinaryIntegerIndividual, self).__init__(genes, parent, statistic)
        
        self._phenome = None
        
        if isinstance(parent, BinaryIntegerIndividual):
            self.resolution = parent.resolution
            self.bits_per_value = parent.bits_per_value
            self.offset = parent.offset
        else:
            self.resolution = int(resolution)
            self.bits_per_value = int(bits_per_value)
            self.offset = int(offset)
    
    @property
    def phenome(self):
        '''Returns the phenome of this individual.
        '''
        if not self._phenome:
            _phenome = [ ]
            if hasattr(self.bits_per_value, '__iter__'):
                i = 0
                for bits in self.bits_per_value:
                    if i + bits > len(self.genome): break
                    _phenome.append(sum(self.genome[i:i+bits]))
                    i += bits
            elif self.bits_per_value:
                i = 0
                bits = self.bits_per_value
                while i + bits <= len(self.genome):
                    _phenome.append(sum(self.genome[i:i+bits]))
                    i += bits
            else:
                _phenome.append(sum(self.genome))
            self._phenome = [self.offset + self.resolution * i for i in _phenome]
        return self._phenome
    
    @property
    def phenome_string(self):
        '''Returns a string representation of the phenome of this individual.
        '''
        return '[' + ', '.join('%d' % i for i in self.phenome) + ']'

class BinarySpecies(Species):
    '''Provides individuals with fixed- or variable-length genomes of
    binary values. Each gene has the value ``0`` or ``1``.
    '''
    name = 'binary'
    
    def __init__(self, cfg, eval_default):
        super(BinarySpecies, self).__init__(cfg, eval_default)
        # Make some names public within the execution context
        self.public_context = {
            'random_binary': self.init_random,
            'random_real_binary': self.init_random_real,
            'random_integer_binary': self.init_random_integer,
            'binary_zero': self.init_zero,
            'binary_one': self.init_one,
            'binary_toggle': self.init_toggle
        }
    
    def _len(self, length, shortest, longest):
        '''Returns a randomly selected length for a new individual.'''
        if length is not None: shortest = longest = length
        
        shortest = int(shortest)
        longest = int(longest)

        assert longest >= shortest, \
            "Value of longest (%d) must be higher or equal to shortest (%d)" % (longest, shortest)
        assert shortest > 0, "Shortest must be greater than zero"
        
        return lambda: rand.randrange(shortest, longest+1)
    
    def init_random(self, length=None, shortest=10, longest=10, template=None): #pylint: disable=W0613
        '''Returns instances of `BinaryIndividual` initialised with random bitstrings.
        
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
          
          template : `BinaryIndividual` [optional]
            Unused for this species.
        '''
        def _bit():
            '''Picks a random bit value.'''
            return 0 if rand.random() <= 0.5 else 1
        len_ = self._len(length, shortest, longest)
        while True:
            yield BinaryIndividual([_bit() for _ in xrange(len_())], self)
    
    def init_random_real(self, length=None, shortest=10, longest=10, resolution=0.1, offset=0.0, bits_per_value=None):
        '''Returns instances of `BinaryRealIndividual` initialised with random bitstrings.
        
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
          
          resolution : float [default 0.1]
            The amount each ``1`` bit contributes to its phenome value.
          
          offset : float [default 0.0]
            The base value, equivalent to all bits zero. Every non-zero
            value is larger than this.
          
          bits_per_value : ``int`` or iterable(``int``)
            The number of bits to use for each phenome value.
        '''
        def _bit():
            '''Picks a random bit value.'''
            return 0 if rand.random() <= 0.5 else 1
        len_ = self._len(length, shortest, longest)
        bits_per_value = int(bits_per_value)
        while True:
            yield BinaryRealIndividual([_bit() for _ in xrange(len_())], self, \
                                       resolution, offset, bits_per_value)
    
    def init_random_integer(self, length=None, shortest=10, longest=10, resolution=1, offset=0, bits_per_value=None):
        '''Returns instances of `BinaryIntegerIndividual` initialised with random bitstrings.
        
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
          
          resolution : int [default 1]
            The amount each ``1`` bit contributes to its phenome value.
          
          offset : int [default 0]
            The base value, equivalent to all bits zero. Every non-zero
            value is larger than this.
          
          bits_per_value : ``int`` or iterable(``int``)
            The number of bits to use for each phenome value.
        '''
        def _bit():
            '''Picks a random bit value.'''
            return 0 if rand.random() <= 0.5 else 1
        len_ = self._len(length, shortest, longest)
        while True:
            yield BinaryIntegerIndividual([_bit() for _ in xrange(len_())], self, \
                                          resolution, offset, bits_per_value)
    
    def init_zero(self, length=None, shortest=10, longest=10):
        '''Returns instances of `Individual` initialised with zeros.
        
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
        '''
        len_ = self._len(length, shortest, longest)
        while True:
            yield BinaryIndividual([0] * len_(), self)
    
    def init_one(self, length=None, shortest=10, longest=10):
        '''Returns instances of `Individual` initialised with ones.
        
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
        '''
        len_ = self._len(length, shortest, longest)
        while True:
            yield BinaryIndividual([1] * len_(), self)
    
    def init_toggle(self, length=None, shortest=10, longest=10):
        '''Returns instances of `Individual`. Every second individual (from
        the first one returned) is initialised with ones; the remainder with zeros.
        
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
        '''
        len_ = self._len(length, shortest, longest)
        while True:
            yield BinaryIndividual([1] * len_(), self)
            yield BinaryIndividual([0] * len_(), self)
    
    def mutate_random(self, _source, per_indiv_rate=1.0, per_gene_rate=0.1, genes=None):
        '''Mutates a group of individuals by replacing genes with random values.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          _source : iterable(`Individual`)
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
          
          genes : int
            The exact number of genes to mutate. If `None`, `per_gene_rate` is
            used instead.
        '''
        frand = rand.random
        shuffle = rand.shuffle
        
        do_all_gene = (per_gene_rate >= 1.0)
        do_all_indiv = (per_indiv_rate >= 1.0)
        
        genes = int(genes or 0)
        
        for indiv in _source:
            if do_all_indiv or frand() < per_indiv_rate:
                new_genes = list(indiv.genome)
                source = xrange(len(new_genes))
                
                if genes:
                    do_all_gene = True
                    source = list(source)
                    shuffle(source)
                    source = islice(source, genes)
                
                for i in source:
                    if do_all_gene or frand() < per_gene_rate:
                        new_genes[i] = 0 if frand() < 0.5 else 1
                
                yield type(indiv)(new_genes, indiv, statistic={ 'mutated': 1 })
            else:
                yield indiv
    
    def mutate_bitflip(self, _source, per_indiv_rate=1.0, per_gene_rate=0.1, genes=None):
        '''Mutates a group of individuals by inverting genes.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          _source : iterable(`Individual`)
            A sequence of individuals. Individuals are taken one at a time
            from this sequence and either returned unaltered or cloned and
            mutated.
          
          per_indiv_rate : |prob|
            The probability of any individual being mutated. If an individual
            is not mutated, it is returned unmodified.
          
          per_gene_rate : |prob|
            The probability of any gene being inverted. If an individual is not
            selected for mutation (under `per_indiv_rate`) then this value is
            unused.
          
          genes : int
            The exact number of genes to mutate. If `None`, `per_gene_rate` is
            used instead.
        '''
        frand = rand.random
        shuffle = rand.shuffle
        
        do_all_gene = (per_gene_rate >= 1.0)
        do_all_indiv = (per_indiv_rate >= 1.0)
        
        genes = int(genes or 0)
        
        for indiv in _source:
            if do_all_indiv or frand() < per_indiv_rate:
                new_genes = list(indiv.genome)
                
                source = enumerate(new_genes)
                
                if genes:
                    do_all_gene = True
                    source = list(source)
                    shuffle(source)
                    source = islice(source, genes)
                
                for i, gene in source:
                    if do_all_gene or frand() < per_gene_rate:
                        new_genes[i] = 1 - gene
                
                yield type(indiv)(new_genes, indiv, statistic={ 'mutated': 1 })
            else:
                yield indiv
    
    def mutate_inversion(self, _source, per_indiv_rate=0.1):
        '''Mutates a group of individuals by inverting entire individuals.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          _source : iterable(`Individual`)
            A sequence of individuals. Individuals are taken one at a time
            from this sequence and either returned unaltered or cloned and
            mutated.
          
          per_indiv_rate : |prob|
            The probability of any individual being mutated. If an individual
            is not mutated, it is returned unmodified.
        '''
        frand = rand.random
        
        do_all_indiv = (per_indiv_rate >= 1.0)
        
        for indiv in _source:
            if do_all_indiv or frand() < per_indiv_rate:
                yield type(indiv)([(1 - g) for g in indiv.genome], indiv, statistic={ 'mutated': 1 })
            else:
                yield indiv
    
    def mutate_gap_inversion(self, _source, per_indiv_rate=0.1, length=None, shortest=1, longest=10):
        '''Mutates a group of individuals by inverting segments within
        individuals.
        
        The genes inverted are always contiguous.
        
        .. include:: epydoc_include.txt
        
        :Parameters:
          _source : iterable(`Individual`)
            A sequence of individuals. Individuals are taken one at a time
            from this sequence and either returned unaltered or cloned and
            mutated.
          
          per_indiv_rate : |prob|
            The probability of any individual being mutated. If an individual
            is not mutated, it is returned unmodified.
          
          length : int > 0 [optional]
            The number of genes to invert at each mutation. If left
            unspecified, a random number between `shortest` and `longest`
            (inclusive) is used to determine the length.
          
          shortest : int > 0
            The smallest number of genes that may be inverted at any
            mutation.
          
          longest : int > `shortest`
            The largest number of genes that may be inverted at any
            mutation.
        '''
        len_ = self._len(length, shortest, longest)
        
        frand = rand.random
        irand = rand.randrange
        
        do_all_indiv = (per_indiv_rate >= 1.0)
        
        for indiv in _source:
            if do_all_indiv or frand() < per_indiv_rate:
                length = len_()
                len_indiv = len(indiv.genome)
                max_cut1 = len_indiv - length
                if max_cut1 > 0:
                    cut1 = irand(max_cut1)
                    cut2 = cut1 + length
                else:
                    cut1, cut2 = 0, len_indiv
                new_genes = list(chain(islice(indiv.genome, cut1), \
                                       ((1 - g) for g in islice(indiv.genome, cut1, cut2)), \
                                       islice(indiv.genome, cut2, len(indiv.genome))))
                yield type(indiv)(new_genes, indiv, statistic={ 'mutated': 1 })
            else:
                yield indiv
