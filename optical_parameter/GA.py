import numpy as np
import tmm

# Supporting functions for the optimization.py

def cal_pop_fitness(coating_complex_functions, substrate_complex_function, new_population, min, max, type):

    fitness = np.ones(new_population.shape[0])*(-99999999999)
    for i in range(new_population.shape[0]):
        lamda_size = (max-min)//10+1
        lamdas = np.linspace(min, max, num = lamda_size)
        # print('wavelength ranges is', lamdas)
        reflections = []
        for wa in lamdas:
            refractive_element = [1]
            for k in range(len(coating_complex_functions)):
                refractive_element.append(coating_complex_functions[k](wa))
            refractive_element.append(substrate_complex_function(wa))
            reflections.append(tmm.coh_tmm('s', refractive_element, new_population[i].tolist(), 0, wa)['R'])
        if type == 'Antireflection':
            fitness[i] = 1-np.average(reflections)
        if type == 'Highreflection':
            fitness[i] = np.average(reflections)
    return fitness


def select_mating_pool(pop, fitness, num_parents):
    # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
    parents = np.empty((num_parents, pop.shape[1]))
    for parent_num in range(num_parents):
        max_fitness_idx = np.where(fitness == np.max(fitness))
        max_fitness_idx = max_fitness_idx[0][0]
        parents[parent_num, :] = pop[max_fitness_idx, :]
        fitness[max_fitness_idx] = -99999999999
    return parents

def crossover(parents, offspring_size):
    offspring = np.empty(offspring_size)
    # The point at which crossover takes place between two parents. Usually it is at the center.
    crossover_point = np.uint8(offspring_size[1]/2)+1
    for k in range(offspring_size[0]):
        # Index of the first parent to mate.
        parent1_idx = k%parents.shape[0]
        # Index of the second parent to mate.
        parent2_idx = (k+1)%parents.shape[0]
        # The new offspring will have its first half of its genes taken from the first parent.
        offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
        # The new offspring will have its second half of its genes taken from the second parent.
        offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
    return offspring

def mutation(offspring_crossover):
    # Mutation changes a single gene in each offspring randomly.
    for idx in range(offspring_crossover.shape[0]):
        # The random value to be added to the gene.
        size = (1,offspring_crossover.shape[1]-2)
        random_value = np.random.uniform(-20.0, 20.0, size)
        offspring_crossover[idx, 1:-1] = np.absolute(np.add(offspring_crossover[idx, 1:-1],  random_value))
    return offspring_crossover