# -*- coding: utf-8 -*-
import random
import numpy as np
# network_module içerisindeki statik yapıları ve maliyet fonksiyonunu içe aktarıyoruz
from network_module import calculate_weighted_total_cost, Graph, Vertex

class GeneticAlgorithmRouter:
    def __init__(self, source, target, graph, demand=0, weights=None):
        self.source = source
        self.target = target
        self.graph = graph
        self.demand = demand 
        # GUI'den gelen ağırlıklar (W_delay, W_reliability, W_resource)
        self.weights = weights if weights else {"W_delay": 0.33, "W_reliability": 0.33, "W_resource": 0.34}
        
        # Algoritma parametreleri
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.2

    def find_random_path(self, current_start=None):
        """
        Kısıtlara uyan ve Graph yapısına uygun rastgele bir yol bulur (DFS temelli).
        """
        start_node = current_start if current_start is not None else self.source
        stack = [(start_node, [start_node], {start_node})]
        
        while stack:
            # Rastgele bir daldan ilerle
            idx = random.randint(0, len(stack) - 1)
            (curr, path, visited) = stack.pop(idx)
            
            if curr == self.target:
                return path
            
            # HATA ÇÖZÜMÜ: adj_list[curr] içindeki (neighbor_id, edge_obj) yapısını kullan
            neighbors_list = Graph.adj_list.get(curr, [])
            valid_neighbors = []
            
            for neighbor_tuple in neighbors_list:
                neighbor_id = neighbor_tuple[0] # Tuple'ın ilk elemanı ID'dir
                if neighbor_id not in visited:
                    # Kapasite kontrolü (Demand)
                    v_helper = Vertex(curr, 0, 0)
                    link_info = v_helper.get_link_info(curr, neighbor_id)
                    if link_info:
                        bw = link_info[0] # Bandwidth
                        if bw >= self.demand:
                            valid_neighbors.append(neighbor_id)
            
            if valid_neighbors:
                next_node = random.choice(valid_neighbors)
                new_visited = visited.copy()
                new_visited.add(next_node)
                stack.append((next_node, path + [next_node], new_visited))
                
        return None

    def calculate_fitness(self, path):
        """
        Döküman Bölüm 3'teki formüllere göre 5 parametre ile maliyet hesaplar  [cite: 66-69, 1046].
        """
        try:
            # network_module.calculate_weighted_total_cost 5 argüman bekler
            cost = calculate_weighted_total_cost(
                self.graph, 
                path, 
                self.weights["W_delay"], 
                self.weights["W_reliability"], 
                self.weights["W_resource"]
            )
            return cost
        except Exception:
            return float('inf')

    def crossover(self, parent1, parent2):
        """İki yolun ortak noktalarını bulup çaprazlama yapar."""
        common = [n for n in parent1[1:-1] if n in parent2[1:-1]]
        if not common:
            return parent1 if random.random() < 0.5 else parent2
        
        pivot = random.choice(common)
        idx1, idx2 = parent1.index(pivot), parent2.index(pivot)
        child = parent1[:idx1] + parent2[idx2:]
        
        return child if len(child) == len(set(child)) else parent1

    def mutate(self, path):
        """Yolun bir kısmını kesip rastgele yeni bir rota ekler."""
        if len(path) < 3: return path
        point = random.randint(1, len(path) - 2)
        new_suffix = self.find_random_path(current_start=path[point])
        if new_suffix:
            new_path = path[:point] + new_suffix
            if len(new_path) == len(set(new_path)): return new_path
        return path

    def run_genetic_algorithm(self):
        """GA döngüsünü çalıştırır."""
        # 1. Başlangıç popülasyonu
        population = []
        for _ in range(self.population_size * 2):
            p = self.find_random_path()
            if p: population.append(p)
            if len(population) >= self.population_size: break
            
        if not population: return None

        # 2. Evrimleşme
        for _ in range(self.generations):
            # Fitness'a göre sırala (Düşük maliyet en iyisidir)
            population = sorted(population, key=self.calculate_fitness)
            new_pop = population[:5] # Elitizm: En iyi 5 yolu koru
            
            while len(new_pop) < self.population_size:
                p1, p2 = random.sample(population[:20], 2)
                child = self.crossover(p1, p2)
                if random.random() < self.mutation_rate:
                    child = self.mutate(child)
                new_pop.append(child)
            
            population = new_pop
            
        return min(population, key=self.calculate_fitness)