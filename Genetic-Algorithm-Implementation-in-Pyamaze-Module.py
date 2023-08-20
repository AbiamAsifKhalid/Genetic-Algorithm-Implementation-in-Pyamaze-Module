''' 
CEP-1: Path Planning using Genetic Algorithm
-------------------------------------------------------------------------
The following program implements Genetic Algorithm (GA) in path planning, 
using the module pyamaze to develop the maze and provide GUI for
the path.
--------------------------------------------------------------------------
Written by Abiam Asif Khalid (abiamasifkhalid77@gmail.com) on 2-April-2023.
IDE: Visual Studio Code 1.69.0
Python Version: 3.10.5
'''
from pyamaze import maze,COLOR,agent
import random
pop_size = 200
Grid_rows = 0
Grid_columns = 0

def main():
    # Main Program 
    print("Enter the Data of the Grid")
    row = int(input("Enter the number of rows: "))
    column = int(input("Enter the number of column: "))
    popsize = int(input("Enter the number of population size: "))

    global Grid_rows,Grid_columns, pop_size
    Grid_rows,Grid_columns,population=row,column,pop_size

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
    population = generate_population(popsize)
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

"""
generate_population creates all the chromosomes for the population. 
Generating population only takes place at the start of the Genetic Algorithm
It uses random module to generate population of chromosomes, where the size
of each chromosome is column - 2 (This is to done to prevent random changes 
during mutation to start and end position).
"""
def generate_population(popsize):
    """ 
    popsize --> population size (number of chromosomes)
    """
    population=[] 
    for _ in range (0, pop_size):
        sublist =[]
        sublist= [random.randrange(0,Grid_rows) for _ in range(Grid_columns - 2)]
        population.append(sublist)
    
    return population

"""
generate_population defines the direction of path spawned from each 
chromosome (0-->column first and 1-->row first).
"""
def generate_direction():

    direction = [random.randrange(2) for _ in range (pop_size)]
    return direction

"""
chromosomemaker adds the starting and ending genes for each chromosome
to create accurate paths.
"""
def chromosomemaker(chromosome):
    # chromosome --> each chromosome in population to be completed
    chromo = []
    chromo.append(0)

    for gene in chromosome:
        chromo.append(gene)

    chromo.append(Grid_rows-1)
    return chromo

# Creates path for a given chromosome with column first(0)
def pathvar1(chromosome):
    path=[]
    path.append((1,1))
    step =1
    for a in range(1,Grid_columns):

        b = chromosome[a]
        checkrow = chromosome[a-1]

        if (checkrow- b >= 0):
            while (b <= checkrow):
                path.append((checkrow+1,a+1))
                step+=1
                checkrow-=1   
        else:
            while (b >= checkrow):
                path.append((checkrow+1,a+1))
                step+=1
                checkrow+=1

    if path[step-1][0]== Grid_rows-1:
        path.append((Grid_rows,Grid_columns))
        step+=1
    else:
        while path[step-1][0] != Grid_rows:
            k = path[step-1][0]
            path.append((k+1,Grid_columns))
            k+=1
            step+=1
    return path,step

# Creates path for a given chromosome with row first(1)
def pathvar2(chromosome):
    path=[]

    step=0
    for b in range(0,Grid_columns-1):
        a = chromosome[b]
        checkrow = chromosome[b+1]

        if (checkrow- a >= 0):
            while (a <= checkrow):
                path.append((a+1,b+1))
                step+=1
                a+=1   
        else:
            while (a >= checkrow):
                path.append((a+1,b+1))
                step+=1
                a-=1
    r,c = path[step-1]
    path.append((r,c+1))
    step+=1
    if path[step-1][0]== Grid_rows-1:
        path.append((Grid_rows,Grid_columns))
        step+=1
    else:
        while path[step-1][0] != Grid_rows:
            k = path[step-1][0]
            path.append((k+1,Grid_columns))
            k+=1
            step+=1
    return path,step

'''
Path evaluator decides upon the direction which pathvar function needs
to be called for each chromosome, also determines the for the given chromosome
what are the infeasible steps, turns and steps of the path created.
'''

def pathevaluator(population, direction, mapmaze):
    """
    population --> the population containing all the chromsomes
    direction --> decides whether path moves row first or column first
    mapmaze -->  Has the dictionary where the keys are cells and
                 values is another dictionary with keys=['E','W','N','S'] for
                 East West North South and values will be 0 or 1. 0 means that 
                 direction(EWNS) is blocked. 1 means that direction is open.
                 imported from the pyamaze module.
    """
    inf=[]
    turns=[]
    steps=[]
    for c in range (pop_size):      
        infeas = 0
        turn = 0
        step = 0

        chromosomearray= chromosomemaker(population[c])
        if (direction[c] == 0):
            path,step = pathvar1(chromosomearray)
        elif (direction[c] == 1):
            path,step = pathvar2(chromosomearray)
        steps.append(step-1)

        for i in range (0,Grid_columns-1):
            if (chromosomearray[i] != chromosomearray[i + 1]):
                turn+=1
        turns.append(turn)

        for k in range (0,step-1):
            row,col = path[k]
            if mapmaze[path[k]]['E']==0 and path[k+1]==(row,col+1):
                infeas+=0.25
            elif mapmaze[path[k]]['W']==0 and path[k+1]==(row,col-1):
                infeas+=0.25
            elif mapmaze[path[k]]['N']==0 and path[k+1]==(row-1,col):
                infeas+=0.25
            elif mapmaze[path[k]]['S']==0 and path[k+1]==(row+1,col):
                infeas+=0.25
     
        inf.append(infeas)
    return inf,turns,steps

"""
Normalises the inf, turns and steps and evaluates the fitness with different 
weights for each attribute
"""
def fitnessfn(inf, turns, steps):
    fitness=[] 
    maxinf, maxturns, maxsteps = max(inf), max(turns), max(steps)
    mininf, minturns, minsteps = 0, min(turns), min(steps)

    for j in range (0,pop_size):
        finf = 1 - ((inf[j] - mininf) / (maxinf - mininf))
        fturn = 1 - ((turns[j] - minturns) / (maxturns - minturns))
        flength = 1 - ((steps[j] - minsteps) / (maxsteps - minsteps))

        fitval = 5 * 100 * finf * ((2 * fturn + 2 * flength) / (2 + 2))
        fitness.append(fitval)
    return fitness

"""
sorts the population with most fit first and least fit at last
"""
def sortfitness(fitness, population):
    sortt=[(fitness[i],population[i]) for i in range (0,pop_size)]
    sortt.sort(reverse=True)
    fit =[]
    pop = []

    for f,p in sortt:
        fit.append(f)
        pop.append(p)
    return fit,pop

"""
Creates two daughter chromosomes from two fittest chromosomes 
with most fit chromosome parents at top and second half the 
populated by daughter chromosomes
"""
def crossoverfn(population):
    crossoverlist=[]
    parents = int(pop_size / 2)
    if Grid_columns%2 ==0:
        value = int((Grid_columns-2)/2)
    else:
        value = int((Grid_columns-2)/2) + 1

    for i in range (0, parents,2):
        daughter1=[]
        daughter2 =[]
        for j in  range (0, value):
            daughter1.append(population[i][j]) 
            daughter2.append(population[i + 1][j])
        for k in  range (value, Grid_columns-2):
            daughter1.append(population[i + 1][k])
            daughter2.append(population[i][k])
        crossoverlist.append(daughter1)
        crossoverlist.append(daughter2)
    
    newpop = [population[x] for x in range(parents)]
    for sublist in crossoverlist:
        newpop.append(sublist)
    return newpop
"""
Randomly changes a value of genes at random index for all the population
"""        
def mutation(population):
    index, val = 0,0
    for i in range (0,pop_size,2):
        index = random.randint(0,Grid_columns-3)
        val = random.randint(0,Grid_rows-1)
        population[i].insert(index,val)
    return population

"""
Searches the chromsome with zero infeassible steps.
"""
def solution(inf):
    for i in range(0,pop_size):
        if (inf[i]==0.00) :
            return i
    return 0

main()