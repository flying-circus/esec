from tests import *
from esec.generators import selectors, joiners
from esec.context import rand, notify

def test_selectors_max():
    population = make_pop_max()
    yield check_selectors_All, population
    yield check_selectors_Best_max, population
    yield check_selectors_Worst_max, population
    yield check_selectors_Tournament_2, population
    yield check_selectors_Tournament_3, population
    yield check_selectors_Tournament_5, population
    yield check_selectors_UniformRandom, population
    yield check_selectors_UniformShuffle, population
    yield check_selectors_FitnessProportional, population
    yield check_selectors_RankProportional, population
    yield check_selectors_BestOfTuple, population, make_best_pop_max()
    
def test_selectors_min():
    population = make_pop_min()
    yield check_selectors_All, population
    yield check_selectors_Best_min, population
    yield check_selectors_Worst_min, population
    yield check_selectors_Tournament_2, population
    yield check_selectors_Tournament_3, population
    yield check_selectors_Tournament_5, population
    yield check_selectors_UniformRandom, population
    yield check_selectors_UniformShuffle, population
    yield check_selectors_FitnessProportional, population
    yield check_selectors_RankProportional, population
    yield check_selectors_BestOfTuple, population, make_best_pop_min()
    

def check_selectors_All(population):
    _gen = selectors.All(iter(population))
    offspring = [next(_gen) for _ in xrange(50)]
    print "len(offspring) = %d, expected = 50" % len(offspring)
    assert len(offspring) == 50, "Did not select expected number of individuals"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    
    _gen = selectors.All(iter(population))
    offspring = list(_gen)
    print "len(offspring) = %d, len(population) = %d" % (len(offspring), len(population))
    assert len(offspring) == len(population), "Did not select all individials"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    
def check_selectors_Best_max(population):
    _gen = selectors.Best(iter(population))
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    print ['[fit=%s]' % i.fitness for i in offspring]
    print
    print ['[fit=%s]' % i.fitness for i in population]
    print
    assert all((i==j for i,j in zip(offspring, reversed(population[-10:])))), "Did not select correct individuals"
    
    _gen = selectors.Best(iter(population), only=True)
    offspring = [next(_gen) for _ in xrange(10)]
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all((i==population[-1] for i in offspring)), "Did not select best individual"

def check_selectors_Best_min(population):
    _gen = selectors.Best(iter(population))
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    print ['[fit=%s]' % i.fitness for i in offspring]
    print
    print ['[fit=%s]' % i.fitness for i in population]
    print
    assert all((i==j for i,j in zip(offspring, population[:10]))), "Did not select correct individuals"
    
    _gen = selectors.Best(iter(population), only=True)
    offspring = [next(_gen) for _ in xrange(10)]
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all((i==population[0] for i in offspring)), "Did not select best individual"

def check_selectors_Worst_max(population):
    _gen = selectors.Worst(iter(population))
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all((i==j for i,j in zip(offspring, population[:10]))), "Did not select correct individuals"

    _gen = selectors.Worst(iter(population), only=True)
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all((i==population[0] for i in offspring)), "Did not select worst individual"

def check_selectors_Worst_min(population):
    _gen = selectors.Worst(iter(population))
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all((i==j for i,j in zip(offspring, reversed(population[-10:])))), "Did not select correct individuals"

    _gen = selectors.Worst(iter(population), only=True)
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all((i==population[-1] for i in offspring)), "Did not select worst individual"

def check_selectors_Tournament_2(population):
    _gen = selectors.Tournament(iter(population), 2, replacement=True)
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    
    _gen = selectors.Tournament(iter(population), 2, replacement=False)
    offspring = list(_gen)
    print "len(offspring) = %d, len(population) = %d" % (len(offspring), len(population))
    assert len(offspring) == len(population), "Did not select all individials"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    assert len(set(offspring)) == len(offspring), "Individuals are not all unique"
    fit = [i.fitness.simple for i in offspring]
    print "fit[:50] = %d, fit[50:] = %d" % (sum(fit[:50]), sum(fit[50:]))
    assert sum(fit[:50]) > sum(fit[50:]), "Average fitness is not better in early selections"

def check_selectors_Tournament_3(population):
    _gen = selectors.Tournament(iter(population), 3, replacement=True)
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    
    _gen = selectors.Tournament(iter(population), 3, replacement=False)
    offspring = list(_gen)
    print "len(offspring) = %d, len(population) = %d" % (len(offspring), len(population))
    assert len(offspring) == len(population), "Did not select all individials"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    assert len(set(offspring)) == len(offspring), "Individuals are not all unique"
    fit = [i.fitness.simple for i in offspring]
    print "fit[:50] = %d, fit[50:] = %d" % (sum(fit[:50]), sum(fit[50:]))
    assert sum(fit[:50]) > sum(fit[50:]), "Average fitness is not better in early selections"

def check_selectors_Tournament_5(population):
    _gen = selectors.Tournament(iter(population), 5, replacement=True)
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    
    _gen = selectors.Tournament(iter(population), 5, replacement=False)
    offspring = list(_gen)
    print "len(offspring) = %d, len(population) = %d" % (len(offspring), len(population))
    assert len(offspring) == len(population), "Did not select all individials"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    assert len(set(offspring)) == len(offspring), "Individuals are not all unique"
    fit = [i.fitness.simple for i in offspring]
    print "fit[:50] = %d, fit[50:] = %d" % (sum(fit[:50]), sum(fit[50:]))
    assert sum(fit[:50]) > sum(fit[50:]), "Average fitness is not better in early selections"
    
def check_selectors_UniformRandom(population):
    _gen = selectors.UniformRandom(iter(population), replacement=True)
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    
def check_selectors_UniformShuffle(population):
    _gen = selectors.UniformRandom(iter(population), replacement=False)
    offspring = list(_gen)
    print "len(offspring) = %d, len(population) = %d" % (len(offspring), len(population))
    assert len(offspring) == len(population), "Did not select all individials"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    assert len(set(offspring)) == len(offspring), "Individuals are not all unique"
    
def check_selectors_FitnessProportional(population):
    _gen = selectors.FitnessProportional(iter(population), replacement=True)
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    
    _gen = selectors.FitnessProportional(iter(population), replacement=False)
    offspring = list(_gen)
    print "len(offspring) = %d, len(population) = %d" % (len(offspring), len(population))
    assert len(offspring) == len(population), "Did not select all individials"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    assert len(set(offspring)) == len(offspring), "Individuals are not all unique"
    fit = [i.fitness.simple for i in offspring]
    print "fit[:50] = %d, fit[50:] = %d" % (sum(fit[:50]), sum(fit[50:]))
    assert sum(fit[:50]) > sum(fit[50:]), "Average fitness is not better in early selections"
    
def check_selectors_RankProportional(population):
    _gen = selectors.RankProportional(iter(population), replacement=True)
    offspring = [next(_gen) for _ in xrange(10)]
    print "len(offspring) = %d, expected = 10" % len(offspring)
    assert len(offspring) == 10, "Did not select expected number of individuals"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    
    _gen = selectors.RankProportional(iter(population), replacement=False)
    offspring = list(_gen)
    print "len(offspring) = %d, len(population) = %d" % (len(offspring), len(population))
    assert len(offspring) == len(population), "Did not select all individials"
    assert all([i in population for i in offspring]), "Some individuals not in original population"
    assert len(set(offspring)) == len(offspring), "Individuals are not all unique"
    fit = [i.fitness.simple for i in offspring]
    print "fit[:50] = %d, fit[50:] = %d" % (sum(fit[:50]), sum(fit[50:]))
    assert sum(fit[:50]) > sum(fit[50:]), "Average fitness is not better in early selections"
    
def check_selectors_BestOfTuple(population, best_population):
    _gen = joiners.DistinctRandomTuples([best_population, population, population], \
                                        ['best_population', 'population', 'population'])
    _gen = selectors.BestOfTuple(_gen)
    offspring = list(_gen)
    print "len(offspring) = %d, len(population) = %d" % (len(offspring), len(best_population))
    assert len(offspring) == len(best_population), "Did not select all individials"
    assert all([i in best_population for i in offspring]), "Some individuals not in original population"
