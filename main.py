import pygame
import copy
from Network import Network
from Pipe import Pipe
from Bird import Bird

pygame.init()

# -------------------
# Constants
# -------------------
GRAVITY = 800
JUMP_FORCE = -300
PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_SPAWN_TIME = 1.5

# -------------------
# Window
# -------------------
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird AI - Genetic Algorithm")

clock = pygame.time.Clock()
FPS = 60


# -------------------
# Collision
# -------------------

def check_collision(bird, pipe):
    if bird.x + bird.radius > pipe.x and bird.x - bird.radius < pipe.x + PIPE_WIDTH:
        if bird.y - bird.radius < pipe.height or \
                bird.y + bird.radius > pipe.height + PIPE_GAP:
            return True
    return False


# -------------------
# Genetic Algorithm
# -------------------

def create_new_generation(birds_dict):
    """
    Create a new generation based on the previous generation's performance
    """
    # Sort birds by score (fitness)
    sorted_birds = sorted(birds_dict.items(), key=lambda x: x[0].score, reverse=True)

    # Keep top performers
    num_keep = 10

    # Extract top performers
    top_performers = sorted_birds[:num_keep]

    print(f"\n=== Generation Complete ===")
    print(f"Top Score: {top_performers[0][0].score}")
    print(f"Average Score: {sum(bird.score for bird, _ in sorted_birds) / len(sorted_birds):.2f}")
    print(f"Median Score: {sorted_birds[len(sorted_birds) // 2][0].score}")

    # Create new population
    new_birds = {}

    # 1. Elite: Keep the best performers as-is (no mutation)
    for i in range(num_keep):
        bird, network = top_performers[i]
        new_bird = Bird(100, HEIGHT // 2)
        new_network = copy.deepcopy(network)
        new_birds[new_bird] = new_network
        print(f"Elite {i + 1}: Score {bird.score}")

    # 2. Breed: Create offspring from top performers
    for i in range(num_keep):
        # Select two random parents from top performers
        parent = top_performers[i]

        for j in range(99):
            new_bird = Bird(100, HEIGHT // 2)

            child_network = copy.deepcopy(parent[1])

            # Mutation rate decreases as we get better performers
            base_mutation = 0.5
            if top_performers[0][0].score > 10:
                mutation_rate = base_mutation * 0.5
            elif top_performers[0][0].score > 5:
                mutation_rate = base_mutation * 0.7
            else:
                mutation_rate = base_mutation

            child_network.mutate(mutation_rate)

            new_birds[new_bird] = child_network

    return new_birds


# -------------------
# Game State
# -------------------

def reset_game():
    """Reset pipes and spawn timer"""
    return [Pipe(WIDTH), Pipe(WIDTH + PIPE_WIDTH + 200)], 0


# -------------------
# Main Training Loop
# -------------------

POPULATION = 1000  # Start with smaller population for faster training
generation = 1
birds = {Bird(100, HEIGHT // 2): Network() for _ in range(POPULATION)}
pipes, spawn_timer = reset_game()
next_pipe = None

running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # Use actual delta time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Press SPACE to skip to next generation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Kill all remaining birds to force new generation
                for bird in birds:
                    bird.dead = True

    screen.fill((0, 0, 0))  # Sky blue background

    # Spawn pipes
    spawn_timer += dt
    if spawn_timer >= PIPE_SPAWN_TIME:
        pipes.append(Pipe(WIDTH + PIPE_WIDTH + 200))
        spawn_timer = 0

    # Get next pipe for AI decision-making
    if next_pipe:
        if next_pipe.x + PIPE_WIDTH < 100:
            for bird in birds:
                if not bird.dead:
                    bird.score += 1
            next_pipe.passed = True

    for pipe in pipes:
        if pipe.x + PIPE_WIDTH > 100:
            next_pipe = pipe
            break

    # Update birds
    alive_count = 0
    for bird in birds:
        if bird.dead:
            continue

        alive_count += 1

        # AI decision
        if next_pipe:
            # Normalize inputs for better neural network performance
            normalized_bird_y = bird.y / HEIGHT
            normalized_velocity = (bird.velocity + 500) / 1000  # Normalize velocity range better
            normalized_distance = (next_pipe.x - bird.x) / WIDTH
            normalized_gap = next_pipe.height / HEIGHT

            output = birds[bird].forward(
                normalized_bird_y,
                normalized_velocity,
                normalized_distance,
                normalized_gap
            )
            if output > 0.9:  # Threshold for jumping
                bird.jump()

        bird.update(dt)

        # Check collisions with pipes
        for pipe in pipes:
            if check_collision(bird, pipe):
                bird.dead = True

        # Check ground and ceiling collision
        if bird.y - bird.radius < 0 or bird.y + bird.radius > HEIGHT:
            bird.dead = True

    # Update and draw pipes
    for pipe in pipes:
        pipe.update(dt)
        pipe.draw(screen)

    pipes = [pipe for pipe in pipes if not pipe.offscreen()]

    # Draw birds
    for bird in birds:
        if not bird.dead:
            bird.draw(screen)

    # Display stats
    font = pygame.font.SysFont("Arial", 24)

    text_gen = font.render(f"Generation: {generation}", True, (255, 255, 255))
    text_alive = font.render(f"Alive: {alive_count}/{POPULATION}", True, (255, 255, 255))

    # Find the best current score
    best_score = max(bird.score for bird in birds)
    text_best = font.render(f"Best Score: {best_score}", True, (255, 255, 255))

    screen.blit(text_gen, (20, 20))
    screen.blit(text_alive, (20, 50))
    screen.blit(text_best, (20, 80))

    # Instructions
    small_font = pygame.font.SysFont("Arial", 16)
    instruction = small_font.render("Press SPACE to skip generation", True, (200, 200, 200))
    screen.blit(instruction, (20, HEIGHT - 30))

    pygame.display.flip()

    # Check if generation is complete (all birds dead)
    if alive_count == 0:
        # Create new generation
        birds = create_new_generation(birds)
        pipes, spawn_timer = reset_game()
        generation += 1

pygame.quit()
