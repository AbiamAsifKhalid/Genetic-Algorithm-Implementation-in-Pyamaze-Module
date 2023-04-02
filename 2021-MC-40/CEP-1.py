''' 
CEP-1: Path Planning using Genetic Algorithm
-------------------------------------------------------------------------
The following program implements Genetic Algorithm (GA) in path planning, 
using the module pyamaze to develop the maze and provide GUI for
the path. The Main Program uses the functions from the 
--------------------------------------------------------------------------
Written by Abiam Asif Khalid (abiamasifkhalid77@gmail.com) on 2-April-2023.
IDE: Visual Studio Code 1.69.0
Python Version: 3.10.5
'''

from pyamaze import maze,COLOR,agent
from GeneticAlgorithmModule import *

# Main Program 
print("Enter the Data of the Grid")
row = int(input("Enter the number of rows: "))
column = int(input("Enter the number of column: "))
popsize = int(input("Enter the number of population size: "))

# Creating/Loading the maze and agent with starting point(1,1)
m=maze(row, column)
m.CreateMaze(row, column, theme=COLOR.dark, loopPercent=100, pattern ="h")
# m.CreateMaze(row, column, theme=COLOR.light, loadMaze="maze--2023-04-01--14-50-12.csv")
a=agent(m, x=1, y=1, footprints = True)

# Iteration -> The total generations in GA
iteration, slnfound = 0,0

""" 
Population is the list of all chromosomes in a generation, direction variable
represents whether the path will be column first(0) or row first(1).
The inf(Infeasible steps), turn, step(lenght of path) are the parameters for 
fitness function.
"""
population = generate_population(row,column,popsize)
direction = generate_direction()
inf,turns,steps= pathevaluator(population, direction, m.maze_map)

fitness = fitnessfn(inf, turns, steps)

while (slnfound == 0 and iteration<2000):

    fitness,population=sortfitness(fitness, population)
    iteration+=1
    population = crossoverfn(population)
    population = mutation(population)

    direction = generate_direction()
    inf,turns,steps = pathevaluator(population, direction, m.maze_map)
    fitness,population = sortfitness(fitness, population)
    
    print(f"{iteration}\t{direction[0]}\t{fitness[0]:.2f}\t{inf[0]}\t{turns[0]}\t{steps[0]}\n")
    with open("fitness2.csv", "a") as f:
       f.write(f"{iteration},{fitness[0]:.2f},{inf[0]:.2f},{turns[0]},{steps[0]}\n")
    
    fitness = fitnessfn(inf, turns, steps)
    inf,turns,steps = pathevaluator(population, direction, m.maze_map)
    slnfound = solution(inf)

if slnfound:
    # Since the Chromosome has colums-2 elements chromosomemaker func. is used to complete the chromosome
    chromosome = chromosomemaker(population[slnfound])
    print(f"Solution found at: Iteration no. {iteration+1}")
    print(f"Chromosome No: {slnfound}\t{direction[slnfound]}\t{fitness[slnfound]:.2f}\t{inf[slnfound]}\t{turns[slnfound]}\t{steps[slnfound]}\n")
    print(list(map(lambda x:x+1, chromosome)))

    if (direction[slnfound] == 0):
        path,step = pathvar1(chromosome)
    else:
        path,step = pathvar2(chromosome) 
    m.tracePath({a:path})  
    m.run()


else:
    print("No feasible path found.")

