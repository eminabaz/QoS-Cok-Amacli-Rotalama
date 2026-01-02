# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np

# Senin modüllerin
from network_module import GenerateGraph, Graph, calculate_metrics, calculate_weighted_total_cost
import aco_algorithm
import GA_Algorithm
from q_learn import QLearningAgent

class QoSRouterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QoS-Aware Intelligent Routing")
        self.root.geometry("1450x900")
        self.root.configure(bg="#0F172A")

        self._theme()

        # Graf yapısını yükle
        self.graph_obj = GenerateGraph().generate()
        self.nx_graph = self._to_nx()
        self.pos = nx.spring_layout(self.nx_graph, seed=42, k=0.15)

        nodes = sorted(self.nx_graph.nodes)
        self.src_var = tk.IntVar(value=nodes[0])
        self.dst_var = tk.IntVar(value=nodes[-1])
        self.algo_var = tk.StringVar(value="ACO")

        self.w_delay = tk.DoubleVar(value=0.33)
        self.w_rel = tk.DoubleVar(value=0.33)
        self.w_res = tk.DoubleVar(value=0.34)
        self.demand_var = tk.DoubleVar(value=100.0)

        self._ui(nodes)
        self._draw()

    def _theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.bg = "#0F172A"
        self.card = "#111827"
        self.text = "#E5E7EB"
        self.accent = "#38BDF8"
        style.configure("TFrame", background=self.bg)
        style.configure("TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 12))
        style.configure("TLabelframe", background=self.card)
        style.configure("TLabelframe.Label", background=self.card, foreground=self.accent, font=("Segoe UI", 13, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 13, "bold"), padding=6)

    def _to_nx(self):
        G = nx.Graph()
        for n in Graph.vertices:
            G.add_node(n)
        for u, neigh in Graph.adj_list.items():
            for v in neigh:
                G.add_edge(u, v[0])
        return G

    def _normalize_weights(self):
        total = self.w_delay.get() + self.w_rel.get() + self.w_res.get()
        if total == 0: return 0.33, 0.33, 0.34
        return (self.w_delay.get() / total, self.w_rel.get() / total, self.w_res.get() / total)

    def _ui(self, nodes):
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        left = ttk.LabelFrame(main, text=" Routing Control ", padding=16)
        left.pack(side=tk.LEFT, fill=tk.Y)

        self._combo(left, "Source Node (S)", self.src_var, nodes)
        self._combo(left, "Destination Node (D)", self.dst_var, nodes)
        self._combo(left, "Algorithm Selection", self.algo_var, ["ACO", "GA", "Q-Learning"])

        ttk.Separator(left).pack(fill="x", pady=12)
        ttk.Label(left, text="Traffic Demand (Mbps)", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Spinbox(left, from_=1, to=1000, textvariable=self.demand_var, font=("Segoe UI", 12)).pack(fill=tk.X, pady=6)

        ttk.Separator(left).pack(fill="x", pady=12)
        ttk.Label(left, text="QoS Weights (W1, W2, W3)", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self._scale(left, "W1: Delay", self.w_delay)
        self._scale(left, "W2: Reliability", self.w_rel)
        self._scale(left, "W3: Resource", self.w_res)

        ttk.Button(left, text="▶ RUN ROUTING", style="Accent.TButton", command=self._run).pack(fill=tk.X, pady=18)

        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))

        self.result = ttk.LabelFrame(right, text=" Routing Results ", padding=14)
        self.result.pack(fill=tk.X)
        self.res_lbl = ttk.Label(self.result, font=("Consolas", 11), justify="left")
        self.res_lbl.pack(anchor="w")

        self.fig, self.ax = plt.subplots(figsize=(9, 7))
        self.fig.patch.set_facecolor(self.bg)
        self.ax.set_facecolor(self.bg)
        self.ax.axis("off")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _combo(self, parent, text, var, values):
        ttk.Label(parent, text=text, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(6, 0))
        ttk.Combobox(parent, values=values, textvariable=var, state="readonly", font=("Segoe UI", 11)).pack(fill=tk.X, pady=4)

    def _scale(self, parent, text, var):
        ttk.Label(parent, text=text).pack(anchor="w")
        tk.Scale(parent, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, variable=var,
                 bg=self.card, fg=self.text, highlightthickness=0).pack(fill=tk.X)

    def _run(self):
        # Arayüzün donmaması için thread kullanıyoruz
        threading.Thread(target=self._logic, daemon=True).start()

    def _logic(self):
        try:
            w1, w2, w3 = self._normalize_weights()
            s, d = self.src_var.get(), self.dst_var.get()
            mbps = self.demand_var.get()
            algo = self.algo_var.get()

            path = None
            if algo == "ACO":
                # ACO'ya w1, w2, w3 ve mbps bilgisini gönderiyoruz
                aco_ayarlari = {
                  "demand": mbps,        # Arayüzden gelen Mbps değeri
                  "num_ants": 20,       # Varsayılan karınca sayısı
                  "num_iters": 15,      # Varsayılan iterasyon
                  "alpha": 1.0,         # Feromon ağırlığı
                  "beta": 2.0,          # Sezgisel bilgi ağırlığı
                  "rho": 0.1,           # Buharlaşma katsayısı
                  "q0": 0.3             # Keşif oranı
                  }
                res = aco_algorithm.run_aco(self.graph_obj, s, d, w1, w2, w3)
                path = res.get("best_path")
            elif algo == "GA":
                # GA'ya mbps ve ağırlıkları gönderiyoruz
                ga = GA_Algorithm.GeneticAlgorithmRouter(s, d, self.graph_obj, mbps, {"W_delay": w1, "W_reliability": w2, "W_resource": w3})
                path = ga.run_genetic_algorithm()
            elif algo == "Q-Learning":
                # Q-Learning eğitim ve yol bulma
                agent = QLearningAgent(self.graph_obj, w1, w2, w3)
                agent.train(s, d, mbps, episodes=500) # Hız için 500 episode
                path = agent.get_best_path(s, d, mbps)

            if not path or len(path) < 2:
                self.root.after(0, lambda: messagebox.showwarning("Warning", f"{mbps} Mbps için uygun yol bulunamadı!"))
                return

            # Ortak metrik fonksiyonunu (senin yazdığın) çağırıyoruz
            m = calculate_metrics(self.graph_obj, path)
            total_cost = calculate_weighted_total_cost(self.graph_obj, path, w1, w2, w3)

            self.root.after(0, lambda: self._final(path, m, total_cost, w1, w2, w3))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Calculation Error", str(e)))

    def _final(self, path, m, total_cost, w1, w2, w3):
        self._draw(path)
        self.res_lbl.config(text=(
            f"Algorithm: {self.algo_var.get()} | Demand: {self.demand_var.get()} Mbps\n"
            f"Path: {' -> '.join(map(str, path))}\n"
            f"----------------------------------------------------------------------\n"
            f"METRICS (S-D Processing Delays Excluded):\n"
            f"  Total Delay: {m['total_delay']:.2f} ms | Reliability Cost: {m['reliability_cost']:.4f}\n"
            f"  Resource Cost: {m['resource_cost']:.2f}\n"
            f"----------------------------------------------------------------------\n"
            f"WEIGHTS: W1={w1:.2f}, W2={w2:.2f}, W3={w3:.2f}\n"
            f"TOTAL WEIGHTED COST: {total_cost:.4f}"
        ))

    def _draw(self, path=None):
        self.ax.clear()
        self.ax.axis("off")
        nx.draw_networkx_nodes(self.nx_graph, self.pos, node_size=20, node_color="#CBD5E1", ax=self.ax)
        nx.draw_networkx_edges(self.nx_graph, self.pos, edge_color="#475569", alpha=0.2, ax=self.ax)

        if path:
            colors = {"ACO": "#22C55E", "GA": "#F59E0B", "Q-Learning": "#A855F7"}
            edges = list(zip(path[:-1], path[1:]))
            nx.draw_networkx_edges(self.nx_graph, self.pos, edgelist=edges, width=3,
                                   edge_color=colors[self.algo_var.get()], ax=self.ax)
            nx.draw_networkx_nodes(self.nx_graph, self.pos, nodelist=[self.src_var.get()], node_color="#38BDF8", node_size=40, ax=self.ax)
            nx.draw_networkx_nodes(self.nx_graph, self.pos, nodelist=[self.dst_var.get()], node_color="#EF4444", node_size=40, ax=self.ax)

        self.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    QoSRouterGUI(root)
    root.mainloop()