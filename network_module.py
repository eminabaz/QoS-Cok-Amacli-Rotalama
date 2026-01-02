import pandas as pd
import numpy as np

# --- AYARLAR: DOSYA İSİMLERİ ---
# Not: Bu dosyalar Python koduyla aynı klasörde olmalı
NODE_FILE = "BSM307_317_Guz2025_TermProject_NodeData.csv"
EDGE_FILE = "BSM307_317_Guz2025_TermProject_EdgeData.csv"
DEMAND_FILE = "BSM307_317_Guz2025_TermProject_DemandData.csv"

class Graph:
    vertices = {} 
    vertices_id = {}
    adj_list = {} 

class Vertex:
    def __init__(self, vertex_id, vertex_process_d, vertex_r):
        self.vertex_id = vertex_id
        self.vertex_p_delayi = vertex_process_d
        self.vertex_r = vertex_r

    def add_vertex(self, vertex_id, vertex_process_d, vertex_r):
        if vertex_id not in Graph.vertices:
            new_vertex = Vertex(vertex_id, vertex_process_d, vertex_r)
            Graph.vertices[vertex_id] = new_vertex
            Graph.vertices_id[vertex_id] = []

    def get_link_info(self, source, destination):
        # İki düğüm arasındaki bağlantı bilgisini döndürür
        if source in Graph.adj_list:
            for neighbor, edge_obj in Graph.adj_list[source]:
                if neighbor == destination:
                    return edge_obj.band_width, edge_obj.link_delayi, edge_obj.link_reliabilit
        return None, None, None

    def add_edges(self):
        try:
            # Pandas ile okuma daha güvenli ve hızlıdır
            df = pd.read_csv(EDGE_FILE, sep=None, engine='python', decimal=',')
            # Beklenen Sütunlar: Source, Target, BW, Delay, Reliability
            for index, row in df.iterrows():
                vals = row.values
                u, v = int(vals[0]), int(vals[1])
                bw, delay, rel = float(vals[2]), float(vals[3]), float(vals[4])
                
                if u not in Graph.adj_list: Graph.adj_list[u] = []
                if v not in Graph.adj_list: Graph.adj_list[v] = []
                
                # Grafiğe ekle
                Graph.adj_list[u].append((v, Edge(bw, delay, rel)))
                Graph.adj_list[v].append((u, Edge(bw, delay, rel)))
                
        except FileNotFoundError:
            print(f"HATA: '{EDGE_FILE}' dosyası bulunamadı. Lütfen proje klasörüne ekleyin.")

    def get_neighbors(self, vertex):
        # Sadece komşu ID'lerini döndürür
        if vertex in Graph.adj_list:
            return [n[0] for n in Graph.adj_list[vertex]]
        return []

class Edge:
    def __init__(self, band_width, link_delayi, link_reliability):
        self.band_width = band_width
        self.link_delayi = link_delayi
        self.link_reliabilit = link_reliability

class GenerateGraph:
    def generate(self):
        # Listeleri sıfırla
        Graph.vertices = {}
        Graph.vertices_id = {}
        Graph.adj_list = {}
        
        graph = Vertex(0,0,0) # Dummy init
        
        # 1. Düğümleri Oku
        try:
            df = pd.read_csv(NODE_FILE, sep=None, engine='python', decimal=',')
            for index, row in df.iterrows():
                vals = row.values
                # NodeID, ProcessDelay, Reliability
                graph.add_vertex(int(vals[0]), float(vals[1]), float(vals[2]))
        except FileNotFoundError:
            print(f"HATA: '{NODE_FILE}' dosyası bulunamadı.")
            return None

        # 2. Bağlantıları Oku
        graph.add_edges()
        
        print(f"✅ Ağ Yüklendi: {len(Graph.vertices)} Düğüm.")
        return graph

# --- ORTAK METRİK HESAPLAMA (TÜM GRUP İÇİN) ---
def calculate_metrics(graph_instance, path):
    total_delay = 0.0
    reliability_cost = 0.0
    resource_cost = 0.0
    MAX_BANDWIDTH = 1000.0
    
    start_node = path[0]
    end_node = path[-1]

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        
        # Link Bilgisi
        bw, delay, rel = graph_instance.get_link_info(u, v)
        
        if bw is None: return None # Yol kopuksa

        total_delay += delay
        reliability_cost += -np.log(rel) if rel > 0 else 999
        resource_cost += (MAX_BANDWIDTH / bw)

        # Ara Düğüm Maliyetleri (Başlangıç ve Bitiş Hariç)
        if u != start_node and u != end_node:
            node = Graph.vertices.get(u)
            if node:
                total_delay += node.vertex_p_delayi
                reliability_cost += -np.log(node.vertex_r) if node.vertex_r > 0 else 999

    return {
        'total_delay': total_delay,
        'reliability_cost': reliability_cost,
        'resource_cost': resource_cost
    }

def calculate_weighted_total_cost(graph_instance, path, W_delay, W_reliability, W_resource):
    m = calculate_metrics(graph_instance, path)
    if m is None: return float('inf')
    return (W_delay * m['total_delay']) + (W_reliability * m['reliability_cost']) + (W_resource * m['resource_cost'])
