import numpy as np
import random
import time
import network_module as network
from metrics_calculator import calculate_weighted_link_cost


class QLearningAgent:
    def __init__(self, graph_obj, w_delay, w_rel, w_res):
        self.graph = graph_obj # Yiğitlerin oluşturduğu graph nesnesi
        self.alpha = 0.7 #Öğrenme hızı (Alpha)
        self.gamma = 0.90  # Geleceğe verilen önem (Gamma)
        self.epsilon = 1
        self.epsilon_azalimi = 0.994 #  epsilonun her adımda azalma oranı.
        self.epsilon_min = 0.01 # epsilonun alabileceği min değer
        
        #Bu kısım önem verdiğimiz parametreyi belirlemek için kullanılıyor.
        self.w_delay = w_delay
        self.w_rel = w_rel
        self.w_res = w_res
        # 250 düğüm için Q tablosu (250x250)
        # Başlangıçta hepsi 0
        self.q_table = np.zeros((251, 251)) 

    def get_valid_actions(self, current_node, demand_mbps):
        """
        Gidilebilecek komşuları getirir, ancak bant genişliği yetmeyenleri eler.
        """
        neighbors = self.graph.get_neighbors(current_node)
        valid_actions = []
        
        for neighbor in neighbors: #Burada her bir neighbor bir id değerine denk.
            # Ağ ekibinin kodundaki get_link_info metodunu kullanıyoruz
            bw, delay, rel = self.graph.get_link_info(current_node, neighbor)
            
            # Eğer kapasite talebi karşılıyorsa listeye ekle
            if bw >= demand_mbps:
                valid_actions.append(neighbor)
                
        return valid_actions

    def calculate_cost(self, src, dst, start_node):
        try:
         total_cost = calculate_weighted_link_cost(self.graph, src, dst, self.w_delay, self.w_rel, self.w_res )
        
         
        
        # EĞER src başlangıç düğümüyse, onun işlem gecikmesini ve güvenilirliğini çıkar
         if src == start_node:
            node_start = network.Graph.vertices.get(start_node)
            if node_start:
                start_node_penalty = (
                    self.w_delay * node_start.vertex_p_delayi +
                    self.w_rel * (-np.log(node_start.vertex_r))
                )
                total_cost -= start_node_penalty
                
         return total_cost
    
        except Exception as e:
         print(e)
         return 99999.0
        
    def get_best_path(self, start_node, end_node, demand_mbps):
        path = [start_node]
        current = start_node
        visited = set([start_node]) 
        
        
        
        for _ in range(100): 
            if current == end_node:
                return path
            
            # 1. Komşuları al
            actions = self.get_valid_actions(current, demand_mbps)
            
            # 2. Daha önce gidilmeyenleri filtrele
            unvisited_actions = [a for a in actions if a not in visited]
            
            if unvisited_actions:
                # Gidilmemişler arasından en yüksek Q değerine sahip olanı seç
                q_values = {a: self.q_table[current, a] for a in unvisited_actions}
                best_action = max(q_values, key=q_values.get)
                
                
                path.append(best_action)
                visited.add(best_action)
                current = best_action
            
            else:
                # EĞER BURAYA GİRDİYSE: Gidecek hiç taze yol kalmamış demektir.
                # Zorla geri dönersek sonsuz döngü (8-20-8-20) olur.
                # O yüzden burada "Pes ediyorum" diyip mevcut yolu döndürmesi en doğrusudur.
                print(f"UYARI: {current} düğümünde döngüye girildi (Tüm komşular gezilmiş). Rota sonlandırılıyor.")
                break 
                
        return path

    def train(self, start_node, end_node, demand_mbps, episodes=500):
        
        start = time.time()
        
        for _ in range(episodes):
            state = start_node
            steps = 0
            max_steps = 100

            visited_in_episode = set([start_node])

            while state != end_node and steps < max_steps:
                steps += 1
                
                tum_komsular = self.get_valid_actions(state, demand_mbps)
                actions = [node for node in tum_komsular if node not in visited_in_episode]
                
                
                if not actions: 
                    

                    break
                
                # 2. Eylem Seç (Epsilon-Greedy)
                if random.uniform(0, 1) < self.epsilon:
                    action = random.choice(actions) # Keşfet (Random)
                else:
                    q_values = {a: self.q_table[state, a] for a in actions}
                    action = max(q_values, key=q_values.get)
                
                
                # 3. Ödül Hesapla (Maliyet ne kadar azsa ödül o kadar büyük)
                cost = self.calculate_cost(state, action, start_node)
                
                if action == end_node:
                    reward = 10000
                else: 
                    reward = -cost
                

                # Geleceği kontrol et: Action'a gidersem oradan çıkış var mı?
                # Bunu anlamak için action'ın komşularına bakarken "visited" listesini de hesaba katmalıyız.
                gelecek_komsular = self.get_valid_actions(action, demand_mbps)
                
                # Gelecek kontrolü için geçici visited seti oluştur
                temp_visited = visited_in_episode.copy()
                temp_visited.add(action)
                
                # Gelecekteki geçerli hamleler (next_valid_actions)
                next_valid_actions = [n for n in gelecek_komsular if n not in temp_visited]
                

                if action == end_node:
                    next_max = 0 # Hedefe varıldı, gelecek maliyeti yok.
                elif next_valid_actions:
                    # Gelecekte yol varsa en iyisini al
                    next_max = np.max([self.q_table[action, a] for a in next_valid_actions])
                else:
                    # KRİTİK NOKTA: Gidecek yer yok (Dead End).
                    # O yola girmenin geleceği karanlık (-10000 ceza).
                    next_max = -10000 
                
                # Formülü Uygula
                old_value = self.q_table[state, action]
                new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
                
                self.q_table[state, action] = new_value

                # 5. Durumu güncelle
                visited_in_episode.add(action)
                state = action

                
            if (self.epsilon > self.epsilon_min):
             self.epsilon *= self.epsilon_azalimi        
         
        end = time.time()
        gecen_sure = end - start
        return gecen_sure

