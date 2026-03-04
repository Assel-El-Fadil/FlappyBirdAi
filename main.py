import pygame
import copy
from Network import Network
from Pipe import Pipe
from Bird import Bird

pygame.init()

# Window settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird AI - Genetic Algorithm")

clock = pygame.time.Clock()
FPS = 60


# Collision check, TODO: make it only check the nearest pipe
def check_collision(bird, pipe):
    if bird.x + bird.radius > pipe.x and bird.x - bird.radius < pipe.x + pipe.PIPE_WIDTH:
        if bird.y - bird.radius < pipe.height or \
                bird.y + bird.radius > pipe.height + pipe.PIPE_GAP:
            return True
    return False


# Genetic Algorithm
def create_new_generation(birds_dict, base_mutation):
    """
    Create a new generation based on the previous generation's performance
    """
    # Sort birds by score (fitness)
    sorted_birds = sorted(birds_dict.items(), key=lambda x: x[0].score, reverse=True)

    num_keep = 10

    # Extract top performers
    top_performers = sorted_birds[:num_keep]

    print(f"\n=== Generation Complete ===")
    print(f"Top Score: {top_performers[0][0].score}")
    print(f"Average Score: {sum(bird.score for bird, _ in sorted_birds) / len(sorted_birds):.2f}")
    print(f"Median Score: {sorted_birds[len(sorted_birds) // 2][0].score}")

    new_birds = {}

    # Keep the best performers as-is (no mutation)
    for i in range(num_keep):
        bird, network = top_performers[i]
        new_bird = Bird(100, HEIGHT // 2)
        new_network = copy.deepcopy(network)
        new_birds[new_bird] = new_network
        print(f"Elite {i + 1}: Score {bird.score}")

    for i in range(num_keep):
        parent = top_performers[i]

        for j in range(99):
            new_bird = Bird(100, HEIGHT // 2)

            child_network = copy.deepcopy(parent[1])

            # Mutation rate decreases as we get better performers generation by generation
            base_mutation_strength = 0.5

            if top_performers[0][0].score > 1000:
                mutation_rate = base_mutation * 0.5
                mutation_strength = base_mutation_strength * 0.1
            elif top_performers[0][0].score > 100:
                mutation_rate = base_mutation * 0.7
                mutation_strength = base_mutation_strength * 0.5
            elif top_performers[0][0].score > 50:
                mutation_rate = base_mutation * 0.75
                mutation_strength = base_mutation_strength
            elif top_performers[0][0].score > 10:
                mutation_rate = base_mutation * 0.8
                mutation_strength = base_mutation_strength
            else:
                mutation_rate = base_mutation
                mutation_strength = base_mutation_strength

            child_network.mutate(mutation_rate, mutation_strength)

            new_birds[new_bird] = child_network

    return new_birds, mutation_rate


# Game restart for new generations
def reset_game():
    """Reset pipes and spawn timer"""
    return [Pipe(WIDTH), Pipe(WIDTH + pipe.PIPE_WIDTH + 200)], 0


# Main Loop
POPULATION = 1000  # Start with smaller population for faster training
generation = 1
birds = {Bird(100, HEIGHT // 2): Network() for _ in range(POPULATION)}
pipes, spawn_timer = reset_game()
next_pipe = None

base_mutation_rate = 0.75

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Press SPACE to skip to next generation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Kill all remaining birds to force new generation
                for bird in birds:
                    bird.dead = True

    screen.fill((0, 0, 0))  # Black background

    # Spawn pipes
    if pipes[-1].x <= 800:
        pipes.append(Pipe(WIDTH + pipe.PIPE_WIDTH + 200))

    # Get next pipe for AI decision-making
    if next_pipe:
        if next_pipe.x + pipe.PIPE_WIDTH < 100 - bird.radius:
            for bird in birds:
                if not bird.dead:
                    bird.score += 1
            next_pipe.passed = True

    for pipe in pipes:
        if not pipe.passed:
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
            normalized_velocity = (bird.velocity + 500) / 1000
            normalized_distance = abs(next_pipe.x - bird.x) / WIDTH
            normalized_gap = next_pipe.height / HEIGHT
            output = birds[bird].forward(
                normalized_bird_y,
                normalized_velocity,
                normalized_distance,
                normalized_gap
            )
            if output > 0.9:  # Threshold for jumping
                bird.jump()

        bird.update()

        # Check collisions with pipes
        for pipe in pipes:
            if check_collision(bird, pipe):
                bird.dead = True

        # Check ground and ceiling collision
        if bird.y - bird.radius < 0 or bird.y + bird.radius > HEIGHT:
            bird.dead = True

    # Update and draw pipes
    for pipe in pipes:
        pipe.update()
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
        birds, base_mutation_rate = create_new_generation(birds, base_mutation_rate)
        pipes, spawn_timer = reset_game()
        generation += 1

pygame.quit()
