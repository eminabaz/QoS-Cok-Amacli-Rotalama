import numpy as np
from network_module import Graph 

# =====================================================================
# A. TEK BAĞLANTI (U, V) BAZLI HESAPLAMALAR (RL, Artımlı Algoritmalar)
# =====================================================================

def calculate_link_cost(graph_instance, u, v):
    """
    u düğümünden v düğümüne giden tek bir bağlantının üç temel maliyet metriğini hesaplar.
    DİKKAT: Bu fonksiyon u düğümünün tüm maliyetlerini (Gecikme, Güv.) içerir.
    S ve D kısıtlamaları, bu fonksiyonu kullanan Algoritma Ekibi tarafından yönetilmelidir!
    """
    MAX_BANDWIDTH = 1000.0
    
    # 1. Bağlantı Özelliklerini Çekme
    link_bandwidth, link_delay, link_reliability = graph_instance.get_link_info(u, v)

    if link_bandwidth is None:
         raise ValueError(f"Hata: {u} ile {v} arasında geçerli bağlantı bilgisi bulunamadı. Algoritma geçersiz komşu seçti.")
    
    # 2. Düğüm Özelliklerini Çekme (u düğümü)
    current_vertex = Graph.vertices[u]
    
    # --- Gecikme Maliyeti ---
    # Total Delay = Link Delay(u, v) + Processing Delay(u)
    delay_cost = link_delay + current_vertex.vertex_p_delayi
    
    # --- Güvenilirlik Maliyeti ---
    # Reliability Cost = -log(Link Reliability) + -log(Node Reliability)
    reliability_cost = (-np.log(link_reliability)) + (-np.log(current_vertex.vertex_r))
    
    # --- Kaynak Kullanım Maliyeti ---
    resource_cost = MAX_BANDWIDTH / link_bandwidth
    
    return {
        'delay': delay_cost,
        'reliability_cost': reliability_cost,
        'resource_cost': resource_cost
    }


def calculate_weighted_link_cost(graph_instance, u, v, W_delay, W_reliability, W_resource):
    """ 
    Tek bir bağlantının ağırlıklı toplam maliyetini (Total Cost) döndürür. 
    """
    if round(W_delay + W_reliability + W_resource, 5) != 1.0:
         raise ValueError("Ağırlıkların toplamı 1.0 olmalıdır.")
         
    metrics = calculate_link_cost(graph_instance, u, v)
    
    # Çok Amaçlı Maliyetin Hesaplanması (Weighted Sum Method)
    total_cost = (
        W_delay * metrics['delay'] +
        W_reliability * metrics['reliability_cost'] +
        W_resource * metrics['resource_cost']
    )
    
    return total_cost


# =====================================================================
# B. YOL (PATH) BAZLI HESAPLAMALAR (Final Değerlendirme, Toplu Algoritmalar)
# =====================================================================

def calculate_path_metrics(graph_instance, path):
    """
    Tüm yol (path) için üç temel optimizasyon metriğini (Total Delay, Reliability Cost, Resource Cost) hesaplar.
    Proje kısıtlarını (S ve D düğümlerinin İşlem Gecikmesi hariç) bu fonksiyon yönetir.
    """
    total_delay = 0.0
    reliability_cost = 0.0
    resource_cost = 0.0
    MAX_BANDWIDTH = 1000.0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        
        link_bandwidth, link_delay, link_reliability = graph_instance.get_link_info(u, v)

        if link_bandwidth is None:
             raise ValueError(f"Hata: {u} ile {v} arasında geçerli bağlantı bilgisi bulunamadı. Yol geçersiz.")

        if i > 0: # Sadece i=0 (S düğümü) hariç tutulur. D zaten u olarak atanmaz.
            current_vertex = Graph.vertices[u] 
            
            total_delay += current_vertex.vertex_p_delayi
            
            # Düğüm Güvenilirlik Maliyeti Toplamı (S ve D hariç ara düğümler için)
            reliability_cost += -np.log(current_vertex.vertex_r) 

        total_delay += link_delay

        reliability_cost += -np.log(link_reliability) 

        resource_cost += (MAX_BANDWIDTH / link_bandwidth) 
    
    # A) Kaynak Düğüm (S) Güvenilirliğini Ekleme (i=0'da hariç kalmıştı)
    node_s = Graph.vertices[path[0]]
    reliability_cost += -np.log(node_s.vertex_r)

    # B) Hedef Düğüm (D) Güvenilirliğini Ekleme (path[-1])
    node_d = Graph.vertices[path[-1]]
    reliability_cost += -np.log(node_d.vertex_r)
    
    return {
        'total_delay': total_delay,
        'reliability_cost': reliability_cost,
        'resource_cost': resource_cost
    }


def calculate_weighted_path_cost(graph_instance, path, W_delay, W_reliability, W_resource):
    """
    Tüm yolun ağırlıklı toplam maliyetini (Total Cost) hesaplar.
    Bu, nihai değerlendirme ve uygunluk (fitness) değeridir.
    """
    if round(W_delay + W_reliability + W_resource, 5) != 1.0:
        raise ValueError("Ağırlıkların toplamı 1.0 olmalıdır.")

    # Temel metrikleri path bazlı fonksiyon ile al
    metrics = calculate_path_metrics(graph_instance, path)
    
    # Çok Amaçlı Maliyetin Hesaplanması (Weighted Sum Method)
    total_cost = (
        W_delay * metrics['total_delay'] +
        W_reliability * metrics['reliability_cost'] +
        W_resource * metrics['resource_cost']
    )
    
    return total_cost