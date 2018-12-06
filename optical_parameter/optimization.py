from .models import Pages, Refractiveindex, Extcoeff, Film, NewFilm, OptimalFilmDesign, FormOptimalFilmDesign
from scipy import interpolate
import numpy as np
from .GA import cal_pop_fitness, select_mating_pool, crossover, mutation
import itertools
import tmm as tmm
import math as math
from .classes import OpticalMaterial

def establish_coating(order, coating):
    result = []
    for lay in order:
        result.append(coating[lay])
    return result


# given the set of coating materials and boundaries such as substrate, min and max wavelength, maximumthickness, type, this function can come up of multiple set of coating film design, use the opticalcoating function to find the best layer thicknesses, and find the best result among all of them
def optimizedesign(substrate, coating, design_min, design_max, maxthickness, type):
    maximum_stacks = int(6*maxthickness//(design_max+design_min)) # here 1.5 is selected because it is an very general average refractive index of dielectric materials
    mid_wave = (design_min + design_max) / 2
    if maximum_stacks>4:
        return None
    else:
        refractives = []
        for i in range(len(coating)):
            function = coating[i].get_refractive_function()
            refractives.append(function(mid_wave))
        refractives = np.asarray(refractives)
        index_order = np.argsort(refractives)
        new_refractives = np.sort(refractives)
        delta = []
        for m in range(len(new_refractives)-1):
            delta.append(new_refractives[m+1]-new_refractives[m])
        max_delta = np.amax(delta)
        split_point = np.where(delta==max_delta)[0][0]+1
        split_index = np.split(index_order, [split_point, len(index_order)])
        low_refrac_indexes = split_index[0]
        high_refrac_indexes = split_index[1]
        coating_index_combine = []
        if type =='Antireflection':
            for stack in range(1, maximum_stacks+1):
                coating_index_combine = coating_index_combine+list(itertools.product(low_refrac_indexes, high_refrac_indexes, repeat = stack))

        elif type == 'Highreflection':
            for stack in range(1, maximum_stacks + 1):
                coating_index_combine = list(coating_index_combine + list(itertools.product(high_refrac_indexes, low_refrac_indexes, repeat= stack)))
        else:
            coating_index_combine = []
        # print(coating_index_combine)

        design_results = []
        best_results = []
        if type =='Antireflection':
            for option in coating_index_combine:
                design_coating = establish_coating(option, coating)
                ds, best_result = optimizecoating(substrate, design_coating, design_min, design_max, maxthickness, type)
                design_results.append((design_coating, ds, 1-best_result))
                best_results.append(best_result[0])
        elif type =='Highreflection':
            for option in coating_index_combine:
                design_coating = establish_coating(option, coating)
                ds, best_result = optimizecoating(substrate, design_coating, design_min, design_max, maxthickness, type)
                design_results.append((design_coating, ds, best_result))
                best_results.append(best_result[0])
        else:
            return None
        sort_design_indexes = np.argsort(best_results)
        top_index = sort_design_indexes[len(design_results)-1]
        best_of_best_design = design_results[top_index]
        print(best_of_best_design[0])
        return best_of_best_design

# The genetic algorithm to optimize the thickness of each layer according to the substrate, coating sequence, min and max wavelength range, maximum thickness and type of materials
def optimizecoating(substrate, coating, min, max, maxthickness, type):
    coating_complex_functions = []
    for i in range(len(coating)):
        function = coating[i].get_complex_function()
        coating_complex_functions.append(function)
    substrate_complex_function = substrate.get_complex_function()

    coating_refractive_functions = []
    for i in range(len(coating)):
        function = coating[i].get_refractive_function()
        coating_refractive_functions.append(function)
    substrate_refractive_function = substrate.get_refractive_function()

    medium_wavelength = (min+max)/2

    refractive_medium = [1]
    for i in range(len(coating_refractive_functions)):
        refractive_medium.append(coating_refractive_functions[i](medium_wavelength))
    refractive_medium.append(substrate_refractive_function(medium_wavelength))
    refractive_medium = np.asarray(refractive_medium)

    num_coatings = len(coating)
    sol_per_pop = 50
    num_parents_mating = 20

    pop_size = (sol_per_pop,
                num_coatings)  # The population will have sol_per_pop cromosome where each chromosome has num_weights genes.
    # Creating the initial population, which refers to the thickness
    substrate_paths = np.ones((sol_per_pop, 1)) * np.inf
    coating_paths = np.random.normal(medium_wavelength/4, medium_wavelength/12, size=pop_size)
    system_paths = np.c_[substrate_paths, coating_paths, substrate_paths]
    new_population = system_paths / refractive_medium[:, None].reshape(1, -1)
    num_generations = 10
    for generation in range(num_generations):
        # Measing the fitness of each chromosome in the population.

        fitness = cal_pop_fitness(coating_complex_functions, substrate_complex_function, new_population, min, max, type)
        # Selecting the best parents in the population for mating.
        parents = select_mating_pool(new_population, fitness,
                                        num_parents_mating)

        # Generating next generation using crossover.
        offspring_crossover = crossover(parents,
                                           offspring_size=(pop_size[0] - parents.shape[0], num_coatings + 2))

        # Adding some variations to the offsrping using mutation.
        offspring_mutation = mutation(offspring_crossover)

        # Creating the new population based on the parents and offspring.
        new_population[0:parents.shape[0], :] = parents
        new_population[parents.shape[0]:, :] = offspring_mutation


    # Getting the best solution after iterating finishing all generations.
    # At first, the fitness is calculated for each solution in the final generation.
    fitness = cal_pop_fitness(coating_complex_functions, substrate_complex_function, new_population, min, max, type)
    # Then return the index of that solution corresponding to the best fitness.
    best_match_idx = np.where(fitness == np.max(fitness))
    ds = new_population[best_match_idx, :]
    best_result = fitness[best_match_idx]

    return ds, best_result
