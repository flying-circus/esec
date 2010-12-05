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

'''A Particle Swarm Optimisation plugin.

This plugin provides a Particle Swarm Optimisation species and system definition.
'''

from esec.context import rand
from esec.species.real import RealIndividual, RealSpecies
from math import sqrt

#==============================================================================

class PSOIndividual(RealIndividual):
    '''An `Individual` for PSO particles.
    
    Each individual is a real-valued vector based on `RealIndividual`. The first
    half of the vector contains position values and the second half contains
    velocity values. The phenome of each individual is just the position values,
    making the length of the individual half of the length of the genome. Velocity
    values may be accessed using the `velocities` property.
    '''
    
    @property
    def genome_string(self):
        '''Returns a string representation of the genes of this individual.'''
        return '[' + ', '.join(['%g (%+g)' % i for i in zip(self.phenome, self.velocities)]) + ']'
    
    def __len__(self):
        '''Returns the number of values in the phenome.'''
        return len(self.genome) // 2
    
    @property
    def phenome(self):
        '''Returns the position values for this individual.'''
        return self.genome[:len(self)]
    
    @property
    def position_bounds(self):
        '''Returns the bounds for positions for this individual.'''
        return (self.lower_bounds[:len(self)], self.upper_bounds[:len(self)])
    
    @property
    def velocities(self):
        '''Returns the velocity values for this individual.'''
        return self.genome[len(self):]
    
    @property
    def velocity_bounds(self):
        '''Returns the bounds for velocities for this individual.'''
        return (self.lower_bounds[len(self):], self.upper_bounds[len(self):])
    
    @property
    def phenome_string(self):
        '''Returns a string representation of the phenome of this individual.'''
        return '[' + ', '.join(['%.3f' % p for p in self.phenome]) + ']'

#==============================================================================

class PSOSpecies(RealSpecies):
    '''Provides particles. Each position and velocity is a sequence of 
    double-precision floating-point values between the provided
    ``lowest`` and ``highest`` values (inclusive).
    '''
    
    name = 'pso'
    
    def __init__(self, cfg, eval_default):
        super(PSOSpecies, self).__init__(cfg, eval_default)
        # Make some names public within the execution context
        self.public_context = {
            'random_pso': self.init_random,
            'update_velocity': self.update_velocity,
            'update_position': self.update_position,
            'update_position_clamp': self.update_position_clamp,
            'update_position_wrap': self.update_position_wrap,
            'update_position_bounce': self.update_position_bounce,
        }
    
    def init_random(self, length=2, lowest=-1.0, highest=1.0, zero_velocity=True, \
                    position_bounds=None, velocity_bounds=None, template=None):
        '''Returns instances of `PSOIndividual` initialised with random values.
        
        The value of `bounds` (or `lowest` and `highest`) are stored with the
        individual and are used implicitly for mutation operations involving the
        individual.
        
        :Parameters:
          length : int > 0
            The number of position (or velocity) coordinates to
            include in each particle.
          
          lowest : float or iterable(float)
            The smallest initialisation value of any position coordinate.
            If `zero_velocity` is ``False``, this value is also used for
            velocities.
            
            If a list of values is provided it must be at least
            `longest` long. Otherwise, the last value in the sequence
            will be used for all subsequent positions.
          
          highest : float > `lowest` or iterable(float)
            The largest initialisation value of any position coordinate.
            If `zero_velocity` is ``False``, this value is also used for
            velocities.
            
            If a list of values is provided it must be at least
            `longest` long. Otherwise, the last value in the sequence
            will be used for all subsequent positions.
          
          zero_velocity : bool [optional]
            ``True`` to set all velocities to zero; otherwise, a random
            value between `lowest` and `highest` (inclusive) is used.
          
          position_bounds : ``[lower bounds, upper bounds]`` [optional]
            The hard position limits to keep with the individual.
            If not specified, no limits are applied. Even if specified,
            the `update_position` operator does not enforce limits.
            One of `update_position_clamp`, `update_position_wrap` or
            `update_position_bounce` must be used to enforce boundaries.
            
            The behaviour of particles reaching these limits is
            determined by the operator in use.
          
          velocity_bounds : ``[lower bounds, upper bounds]`` [optional]
            The hard velocity limits to keep with the individual.
            If not specified, velocity is not limited.
            
            The behaviour of particles reaching these limits is
            determined by the operator in use. The `update_velocity`
            operator clamps the new velocity value to these extremes.
          
          template : `PSOIndividual` [optional]
            If provided, used to determine the values for `lowest`
            and `highest`.
        '''
        frand = rand.random
        
        cb = self._convert_bounds
        inf = float('inf')
        length = int(length)
        
        if position_bounds and velocity_bounds:
            bounds = [ cb(position_bounds[0], length) + cb(velocity_bounds[0], length), \
                       cb(position_bounds[1], length) + cb(velocity_bounds[1], length) ]
        elif position_bounds:
            bounds = [ cb(position_bounds[0], length) + cb(-inf, length), \
                       cb(position_bounds[1], length) + cb( inf, length) ]
        elif velocity_bounds:
            bounds = [ cb(-inf, length)               + cb(velocity_bounds[0], length), \
                       cb( inf, length)               + cb(velocity_bounds[1], length) ]
        else:
            bounds = [ cb(-inf, length)               + cb(-inf, length), \
                       cb( inf, length)               + cb( inf, length) ]
        
        if zero_velocity:
            for indiv in self._init(length, None, None, lowest, highest, bounds[0], bounds[1],
                                    lambda low, high, _: frand() * (high - low) + low):
                yield PSOIndividual(indiv.genome + [0] * length, self, indiv.lower_bounds, indiv.upper_bounds)
        else:
            for indiv in self._init(length * 2, None, None, lowest, highest, bounds[0], bounds[1],
                                    lambda low, high, _: frand() * (high - low) + low):
                yield PSOIndividual(indiv.genome, self, indiv.lower_bounds, indiv.upper_bounds)
    
    def update_velocity(self, _source, global_best, w=1.0, inertia=None, c1=2.0, c2=2.0, constriction=False):
        '''A generator that yields one mutated Individual for every JoinedIndividual
        passed in `source`.
        
        Each element of `source` should be a tuple containing the current individual
        and the best value found for that individual.
        
        `global_best` should contain the best individual found.
        
        Velocities are hard limited to their bounds.
        '''
        
        assert isinstance(global_best[0], PSOIndividual), "Expected PSOIndividual for global_best"
        global_best = global_best[0]
        
        frand = rand.random
        
        if inertia != None:
            w = inertia
        if constriction:
            c = c1 + c2
            k = 2 / abs(2 - c - sqrt(c * (c - 4)))
            w *= k
            c1 *= k
            c2 *= k
        
        for joined_individual in _source:
            indiv, indiv_best = joined_individual[:]
            assert isinstance(indiv, PSOIndividual), "Expected PSOIndividual first in each joined individual"
            assert isinstance(indiv_best, PSOIndividual), "Expected PSOIndividual second in each joined individual"
            
            new_velocity = list(indiv.velocities)
            for i, (pos, vel, pbest_pos, gbest_pos, vel_low, vel_high) in \
                enumerate(zip(indiv, new_velocity, indiv_best, global_best, *indiv.velocity_bounds)):
                
                new_vel = w*vel + c1*frand()*(pbest_pos-pos) + c2*frand()*(gbest_pos-pos)
                
                new_velocity[i] = vel_low  if new_vel < vel_low  else \
                                  vel_high if new_vel > vel_high else \
                                  new_vel
                
            yield PSOIndividual(indiv.phenome + new_velocity, indiv)
    
    def _update_position(self, _source, delta, range_handler):
        for indiv in _source:
            new_position = list(indiv)
            new_velocity = list(indiv.velocities)
            
            for i, (pos, vel, pos_low, pos_high) in \
                enumerate(zip(new_position, new_velocity, *indiv.position_bounds)):
                
                new_pos = pos + vel*delta
                
                new_position[i], new_velocity[i] = range_handler(new_pos, vel, pos_low, pos_high)
            
            yield PSOIndividual(new_position + new_velocity, indiv)
    
    def update_position(self, _source, delta=1.0, time_step=None):
        '''A generator that yields one updated particle for every particle in
        `source`.
        '''
        def _range_handler(pos, vel, low, high):
            return (pos, vel)
        
        return self._update_position(_source, delta or time_step, _range_handler)
    
    def update_position_clamp(self, _source, delta=1.0, time_step=None):
        '''A generator that yields one updated particle for every particle in
        `source`.
        '''
        def _range_handler(pos, vel, low, high):
            if pos < low:    return (low, 0.0)
            elif pos > high: return (high, 0.0)
            else:            return (pos, vel)
        
        return self._update_position(_source, delta or time_step, _range_handler)
        
    def update_position_wrap(self, _source, delta=1.0, time_step=None):
        '''A generator that yields one updated particle for every particle in
        `source`.
        '''
        def _range_handler(pos, vel, low, high):
            if pos < low: pos = high - (low - pos)
            elif pos > high: pos = low + (pos - high)
            return (pos, vel)
        
        return self._update_position(_source, delta or time_step, _range_handler)

    def update_position_bounce(self, _source, delta=1.0, time_step=None):
        '''A generator that yields one updated particle for every particle in
        `source`.
        '''
        def _range_handler(pos, vel, low, high):
            if pos < low:    return (low + low - pos, -vel)
            elif pos > high: return (high + high - pos, -vel)
            else:            return (pos, vel)
        
        return self._update_position(_source, delta or time_step, _range_handler)

#==============================================================================

# Add the species class to the list of available species types
import esec.species
esec.species.include(PSOSpecies)

#==============================================================================

PSO_DEF = r'''
FROM random_pso(length=cfg.landscape.size.exact, \
                lowest=cfg.landscape.lower_bounds,highest=cfg.landscape.upper_bounds, \
                position_bounds=[cfg.landscape.lower_bounds, cfg.landscape.upper_bounds], \
                velocity_bounds=[cfg.landscape.lower_bounds, cfg.landscape.upper_bounds]) \
        SELECT (size) population
FROM population SELECT 1 global_best USING best_only
FROM population SELECT (size) p_bests
YIELD population

BEGIN GENERATION
    JOIN population, p_bests INTO pairs USING tuples
    
    FROM pairs SELECT population USING \
         update_velocity(global_best=global_best, w=inertia, c1=c1, c2=c2, constriction=True), \
         update_position_clamp
    
    JOIN population, p_bests INTO pairs USING tuples
    FROM pairs SELECT p_bests USING best_of_tuple
    
    FROM population, global_best SELECT 1 global_best USING best_only
    
    YIELD global_best, population
END GENERATION
'''

#==============================================================================

defaults = {
    'system': {
        'size': 100,
        'definition': PSO_DEF,
        'inertia': 1.0,
        'c1': 2,
        'c2': 2,
    }
}