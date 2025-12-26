import random
import copy

# -------------------------------
# Config
# -------------------------------
POPULATION_SIZE = 50
GENOME_LENGTH = 10  # weights
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.7
GENERATIONS = 100

# -------------------------------
# Define the AI agent
# -------------------------------
class Agent:
    def __init__(self, genome=None):
        # Genome represents the strategy
        self.genome = genome if genome else [random.uniform(-1, 1) for _ in range(GENOME_LENGTH)]
        self.fitness = 0

    def evaluate(self, game_state):
        """
        Evaluate agent in the game.
        Replace this with actual game logic.
        For now, we sum the genome values as a placeholder fitness.
        """
        # Example: score based on genome values (replace with game simulation)
        self.fitness = sum(self.genome)
        return self.fitness

# -------------------------------
# EA functions
# -------------------------------
def select_parents(population):
    """Tournament selection"""
    tournament_size = 3
    parents = []
    for _ in range(len(population)):
        competitors = random.sample(population, tournament_size)
        winner = max(competitors, key=lambda agent: agent.fitness)
        parents.append(winner)
    return parents

def crossover(parent1, parent2):
    """Single-point crossover"""
    if random.random() < CROSSOVER_RATE:
        point = random.randint(1, GENOME_LENGTH - 1)
        child1_genome = parent1.genome[:point] + parent2.genome[point:]
        child2_genome = parent2.genome[:point] + parent1.genome[point:]
        return Agent(child1_genome), Agent(child2_genome)
    else:
        return copy.deepcopy(parent1), copy.deepcopy(parent2)

def mutate(agent):
    """Random mutation"""
    for i in range(GENOME_LENGTH):
        if random.random() < MUTATION_RATE:
            agent.genome[i] += random.uniform(-0.5, 0.5)  # small change
    return agent

def evolve(population, game_state):
    # Fitness & selection
    for agent in population:
        agent.evaluate(game_state)

    parents = select_parents(population)

    # Crossover + Mutation
    next_gen = []
    for i in range(0, len(parents), 2):
        parent1 = parents[i]
        parent2 = parents[i + 1] if i + 1 < len(parents) else parents[0]
        child1, child2 = crossover(parent1, parent2)
        next_gen.append(mutate(child1))
        next_gen.append(mutate(child2))

    return next_gen[:len(population)] 

# -------------------------------
# Main loop
# -------------------------------
def run_evolution(game_state):
    population = [Agent() for _ in range(POPULATION_SIZE)]

    for generation in range(GENERATIONS):
        population = evolve(population, game_state)
        best = max(population, key=lambda agent: agent.fitness)
        print(f"Generation {generation} | Best Fitness: {best.fitness}")

    # Return the best agent
    return max(population, key=lambda agent: agent.fitness)

# -------------------------------
# Example
# -------------------------------
if __name__ == "__main__":
    # Replace with game state object
    dummy_game_state = {}
    best_agent = run_evolution(dummy_game_state)
    print("Best agent genome:", best_agent.genome)
