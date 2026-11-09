"""
Projet : Ordonnancement de maintenance de centrales électriques par Algorithmes Génétiques.

FORMULATION DU PROBLÈME :
L'objectif est de planifier la maintenance de 7 unités sur 4 intervalles de temps.
On cherche à maximiser la réserve minimale d'électricité sur l'année.
Fonction Objective (Fitness) :
Pour un chromosome donné, on calcule la réserve pour chaque intervalle i :
Réserve(i) = Capacité_Totale - Somme(Capacités en maintenance) - Demande(i)
La performance (Fitness) est la plus petite des 4 réserves. 
Si une réserve est négative, la fitness est pénalisée à 0.

ENCODAGE :
Chaque unité est représentée par 4 bits (1 intervalle = 1 bit).
'1' = En maintenance, '0' = En fonctionnement.
Exemple : '1100' pour l'unité 1 signifie maintenance aux intervalles 1 et 2.

OPÉRATEURS (Exigences du sujet) :
- Sélection par Loterie (Roulette Wheel) : probabilité proportionnelle à la fitness.
- Croisement : Un point de coupure, exclusivement entre les blocs de 4 bits.
- Mutation par Inversion : Remplacement d'un bloc de 4 bits par une autre 
  configuration valide (définie dans le tableau du sujet) pour éviter les cédules illogiques.
"""

import random
import matplotlib.pyplot as plt

# --- 1. DONNÉES DU PROBLÈME ---
capacites = [20, 15, 35, 40, 15, 15, 10]
demandes = [80, 90, 65, 70]
capacite_totale = sum(capacites)

# Configurations de maintenance valides (pour éviter les mutations illogiques)
valid_blocks = {
    0: ["1100", "0110", "0011"], # Unité 1 (2 intervalles)
    1: ["1100", "0110", "0011"], # Unité 2 (2 intervalles)
    2: ["1000", "0100", "0010", "0001"], # Unité 3 (1 intervalle)
    3: ["1000", "0100", "0010", "0001"], # Unité 4 (1 intervalle)
    4: ["1000", "0100", "0010", "0001"], # Unité 5 (1 intervalle)
    5: ["1000", "0100", "0010", "0001"], # Unité 6 (1 intervalle)
    6: ["1000", "0100", "0010", "0001"]  # Unité 7 (1 intervalle)
}

# --- 2. FONCTIONS DE BASE ---

def generer_chromosome():
    """Génère un chromosome valide aléatoire (une cédule de base)."""
    chromosome = []
    for i in range(7):
        chromosome.append(random.choice(valid_blocks[i]))
    return chromosome

def calculer_fitness(chromosome):
    """Calcule la réserve minimale (fonction objective)."""
    reserves = []
    for intervalle in range(4):
        puissance_perdue = 0
        for unite in range(7):
            if chromosome[unite][intervalle] == '1':
                puissance_perdue += capacites[unite]
        reserve = capacite_totale - puissance_perdue - demandes[intervalle]
        reserves.append(reserve)
    fitness = min(reserves)
    return max(0, fitness) # Si négatif, fitness = 0

# --- 3. OPÉRATEURS GÉNÉTIQUES ---

def selection_loterie(population, fitness_scores):
    """Méthode de sélection par loterie (Roulette Wheel)."""
    total_fitness = sum(fitness_scores)
    if total_fitness == 0:
        return random.choice(population)
    pick = random.uniform(0, total_fitness)
    current = 0
    for i, fitness in enumerate(fitness_scores):
        current += fitness
        if current > pick:
            return population[i]
    return population[-1]

def croisement(parent1, parent2):
    """Croisement en un point (uniquement entre les blocs de 4 bits)."""
    point = random.randint(1, 6)
    enfant1 = parent1[:point] + parent2[point:]
    enfant2 = parent2[:point] + parent1[point:]
    return enfant1, enfant2

def mutation_inversion(chromosome, taux_mutation=0.1):
    """Mutation par inversion (remplacement par une configuration valide)."""
    chromosome_mute = list(chromosome)
    if random.random() < taux_mutation:
        unite_mutee = random.randint(0, 6)
        options = [b for b in valid_blocks[unite_mutee] if b != chromosome_mute[unite_mutee]]
        if options:
            chromosome_mute[unite_mutee] = random.choice(options)
    return chromosome_mute

# --- 4. ALGORITHME GÉNÉTIQUE PRINCIPAL ---

def algorithme_genetique(taille_pop=50, generations=100, taux_mutation=0.1):
    population = [generer_chromosome() for _ in range(taille_pop)]
    meilleur_chromosome = None
    meilleure_fitness = -1
    historique_fitness = []

    for gen in range(generations):
        fitness_scores = [calculer_fitness(ind) for ind in population]
        max_fit = max(fitness_scores)
        
        if max_fit > meilleure_fitness:
            meilleure_fitness = max_fit
            meilleur_chromosome = population[fitness_scores.index(max_fit)]
            
        historique_fitness.append(meilleure_fitness)
        nouvelle_population = [meilleur_chromosome] # Élitisme
        
        while len(nouvelle_population) < taille_pop:
            parent1 = selection_loterie(population, fitness_scores)
            parent2 = selection_loterie(population, fitness_scores)
            enfant1, enfant2 = croisement(parent1, parent2)
            enfant1 = mutation_inversion(enfant1, taux_mutation)
            enfant2 = mutation_inversion(enfant2, taux_mutation)
            nouvelle_population.extend([enfant1, enfant2])
            
        population = nouvelle_population[:taille_pop]

    return meilleur_chromosome, meilleure_fitness, historique_fitness

# --- 5. EXÉCUTION ET AFFICHAGE ---

if __name__ == "__main__":
    TAUX_MUTATION = 0.1 
    meilleur_individu, score, historique = algorithme_genetique(50, 100, TAUX_MUTATION)
    
    print(f"Réserve minimale garantie : {score} MW\n")
    noms_unites = ["U1", "U2", "U3", "U4", "U5", "U6", "U7"]
    for i, bloc in enumerate(meilleur_individu):
        print(f"Unité {noms_unites[i]} : {bloc}")
        
    print("\nDétail par intervalle :")
    for i in range(4):
        perdue = sum(capacites[u] for u in range(7) if meilleur_individu[u][i] == '1')
        reserve = capacite_totale - perdue - demandes[i]
        print(f"Intervalle {i+1} : Demande={demandes[i]} MW | Perdue={perdue} MW | Réserve={reserve} MW")

    try:
        plt.figure(figsize=(8, 5))
        plt.plot(historique, color='blue', linewidth=2)
        plt.title("Évolution de la fitness")
        plt.xlabel("Générations")
        plt.ylabel("Réserve (MW)")
        plt.grid(True)
        plt.savefig("courbe_convergence.png")
        plt.show()
    except ImportError:
        print("\n[INFO] matplotlib n'est pas installé, le graphique n'a pas pu être généré.")