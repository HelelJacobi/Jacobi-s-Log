import pyglet
import random
import copy

# -------------------------------
# Config
# -------------------------------
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
POPULATION_SIZE = 10
VISION_ZONES = 5
GENOME_LENGTH = VISION_ZONES
MUTATION_RATE = 0.5
CROSSOVER_RATE = 0.7
ELITE_COUNT = 2
OBSTACLE_SPEED = 10
AGENT_SPEED = 5
OBSTACLE_INTERVAL_FRAMES = 30
VISION_HEIGHT = 30
SPAWN_SPACING = 20
GAP_WIDTH = 1
SPAWN_POINTS = list(range(0, WINDOW_WIDTH + 1, SPAWN_SPACING))
GROUP_A = SPAWN_POINTS[::2]
GROUP_B = SPAWN_POINTS[1::2]

# -------------------------------
# Deterministic Obstacle Pattern
# -------------------------------
# Predefined gap positions
PATTERN_SEQUENCE = [
    (GROUP_A, 1), (GROUP_B, 2), (GROUP_A, 3), (GROUP_B, 0),
    (GROUP_A, 2), (GROUP_B, 1), (GROUP_A, 0), (GROUP_B, 3)
]
pattern_index = 0

# -------------------------------
# Agent Definition
# -------------------------------
class Agent:
    def __init__(self, genome=None):
        self.genome = genome if genome else [random.uniform(-0.05, 0.05) for _ in range(GENOME_LENGTH)]
        self.fitness = 0
        self.cycles_survived = 0
        self.x = WINDOW_WIDTH // 2
        self.y = 30
        self.alive = True

    def decide(self, obstacles):
        inputs = [0]*VISION_ZONES
        zone_width = 60
        for obs in obstacles:
            dx = obs['x'] - self.x
            dy = obs['y'] - self.y
            if 0 < dy <= VISION_HEIGHT:
                if dx < -2*zone_width:
                    inputs[0] += 1
                elif dx < -zone_width:
                    inputs[1] += 1
                elif dx < 0:
                    inputs[2] += 1
                elif dx < zone_width:
                    inputs[3] += 1
                else:
                    inputs[4] += 1
        move = sum([w*i for w,i in zip(self.genome, inputs)])
        if move > 0:
            self.x += AGENT_SPEED
        elif move < 0:
            self.x -= AGENT_SPEED
        self.x = max(0, min(WINDOW_WIDTH, self.x))

    def evaluate(self, obstacles):
        if not self.alive:
            return
        self.fitness = self.cycles_survived
        for obs in obstacles:
            if abs(self.x - obs['x']) < 15 and abs(self.y - obs['y']) < 15:
                self.alive = False
                break

# -------------------------------
# Obstacle Row
# -------------------------------
class ObstacleRow:
    def __init__(self, xs):
        self.y = WINDOW_HEIGHT
        self.xs = xs
        self.sprites = [pyglet.shapes.Rectangle(x, WINDOW_HEIGHT, 10, 10, color=(255,0,0), batch=batch) for x in xs]

    def update(self):
        self.y -= OBSTACLE_SPEED
        for sprite in self.sprites:
            sprite.y = self.y

# -------------------------------
# Lil Guy Functions
# -------------------------------
def select_parents(population):
    tournament_size = 3
    parents = []
    for _ in range(len(population)):
        competitors = random.sample(population, tournament_size)
        winner = max(competitors, key=lambda a: a.fitness)
        parents.append(winner)
    return parents

def crossover(p1, p2):
    if random.random() < CROSSOVER_RATE:
        point = random.randint(1, GENOME_LENGTH-1)
        child1 = Agent(p1.genome[:point] + p2.genome[point:])
        child2 = Agent(p2.genome[:point] + p1.genome[point:])
        return child1, child2
    else:
        return copy.deepcopy(p1), copy.deepcopy(p2)

def mutate(agent):
    for i in range(GENOME_LENGTH):
        if random.random() < MUTATION_RATE:
            agent.genome[i] += random.uniform(-0.05, 0.05)
    return agent

def evolve(population):
    population.sort(key=lambda a: a.fitness, reverse=True)
    next_gen = [copy.deepcopy(a) for a in population[:ELITE_COUNT]]  # preserve elites
    parents = select_parents(population)
    while len(next_gen) < len(population):
        p1 = random.choice(parents)
        p2 = random.choice(parents)
        c1, c2 = crossover(p1, p2)
        next_gen.append(mutate(c1))
        if len(next_gen) < len(population):
            next_gen.append(mutate(c2))
    return next_gen[:len(population)]

# -------------------------------
# Pyglet Setup
# -------------------------------
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Evolution/ AI/ InvestmentBuzzword")
batch = pyglet.graphics.Batch()
agent_sprites = []
obstacle_sprites = []
generation_label = pyglet.text.Label('', x=10, y=WINDOW_HEIGHT-20, color=(255,255,255,255))
alive_label = pyglet.text.Label('', x=10, y=WINDOW_HEIGHT-40, color=(255,255,255,255))
max_cycles_label = pyglet.text.Label('', x=10, y=WINDOW_HEIGHT-60, color=(255,255,0,255))

population = [Agent() for _ in range(POPULATION_SIZE)]
obstacle_rows = []
frames = 0
current_generation = 0
spawn_group_toggle = True
generation_max_cycles = 0
wave = 0

# -------------------------------
# Update
# -------------------------------
def update(dt):
    global frames, obstacle_rows, population, current_generation, spawn_group_toggle, generation_max_cycles, wave, pattern_index
    frames += 1

    # Spawn new row
    if frames % OBSTACLE_INTERVAL_FRAMES == 0:
        if wave < 50:
            # Deterministic pattern
            group, gap_idx = PATTERN_SEQUENCE[pattern_index]
            pattern_index = (pattern_index + 1) % len(PATTERN_SEQUENCE)
            gap_start_idx = gap_idx
            gap_indices = group[gap_start_idx:gap_start_idx+GAP_WIDTH]
            row_xs = [x for x in group if x not in gap_indices]
        else:
            # Semi-random but solvable pattern
            group = random.choice([GROUP_A, GROUP_B])
            gap_start_idx = random.randint(0, len(group) - GAP_WIDTH)
            gap_indices = group[gap_start_idx:gap_start_idx + GAP_WIDTH]
            row_xs = [x for x in group if x not in gap_indices]

        obstacle_rows.append(ObstacleRow(row_xs))

    # Update obstacles
    for row in obstacle_rows[:]:
        row.update()
        if row.y <= 0:
            for agent in population:
                if agent.alive:
                    agent.cycles_survived += 1
            for spr in row.sprites:
                spr.delete()
            obstacle_rows.remove(row)
            wave += 1

    all_obstacles = [{'x': x, 'y': row.y, 'sprite': None} for row in obstacle_rows for x in row.xs]

    # Update agents
    alive_count = 0
    for i, agent in enumerate(population):
        if agent.alive:
            agent.decide(all_obstacles)
            agent.evaluate(all_obstacles)
            alive_count += 1
        else:
            if i < len(agent_sprites) and agent_sprites[i] is not None:
                agent_sprites[i].delete()
                agent_sprites[i] = None

        generation_max_cycles = max(generation_max_cycles, agent.cycles_survived)

        if i >= len(agent_sprites):
            agent_sprites.append(pyglet.shapes.Circle(agent.x, agent.y, 10, color=(0,255,0), batch=batch))
        elif agent_sprites[i] is not None:
            agent_sprites[i].x = agent.x
            agent_sprites[i].y = agent.y
            agent_sprites[i].color = (0,255,0)

    best_agent = max(population, key=lambda a: a.cycles_survived)
    if best_agent in population:
        idx = population.index(best_agent)
        if idx < len(agent_sprites) and agent_sprites[idx] is not None:
            agent_sprites[idx].color = (255,255,0)

    max_cycles_label.text = f"Highest Cycles Survived: {wave}"
    generation_label.text = f"Generation: {current_generation}"
    alive_label.text = f"Alive: {alive_count}"

    # Handle generation end
    if alive_count == 0 or wave == 100:
        print("# -------------------------------")
        print(f"Generation {current_generation} evolved. Highest cycle survived: {wave}")
        print(f"Best agent cycles: {generation_max_cycles}")
        print("# -------------------------------")
        if wave == 100:
            print("# -------------------------------")
            print("Lil Guy is perfect now, go away")
            print("# -------------------------------")
            pyglet.app.exit()
        population[:] = evolve(population)
        current_generation += 1
        for spr in agent_sprites:
            if spr:
                spr.delete()
        agent_sprites.clear()
        obstacle_rows.clear()
        frames = 0
        generation_max_cycles = 0
        wave = 0
        pattern_index = 0


# -------------------------------
# Draw Da Tings
# -------------------------------
@window.event
def on_draw():
    window.clear()
    batch.draw()
    generation_label.draw()
    alive_label.draw()
    max_cycles_label.draw()

# -------------------------------
# Run Dodgger
# -------------------------------
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()
