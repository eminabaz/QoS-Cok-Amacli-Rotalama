import random
from network_module import Graph
from metrics_calculator import calculate_link_cost, calculate_weighted_link_cost


def _all_nodes():
    # IDs 0..249 أو 1..250
    return list(Graph.vertices.keys())


def _safe_neighbors(graph, u):
    try:
        return graph.get_neighbors(u) or []
    except Exception:
        return []


def evaluate_path(graph, path, W_delay, W_reliability, W_resource):
    """
    Yol metriklerini hesaplar.
    NOT: Kaynak (S) ve hedef (D) düğümlerinin işlem gecikmesi alınmayacak.
    """
    total_delay = 0.0
    total_rel = 0.0
    total_res = 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        m = calculate_link_cost(graph, u, v)
        total_delay += m["delay"]
        total_rel += m["reliability_cost"]
        total_res += m["resource_cost"]

    # S'nin işlem gecikmesini çıkar (D zaten eklenmez)
    if len(path) >= 2:
        s = path[0]
        total_delay -= Graph.vertices[s].vertex_p_delayi

    total_cost = (
        W_delay * total_delay +
        W_reliability * total_rel +
        W_resource * total_res
    )
    return total_delay, total_rel, total_res, total_cost

    
def _init_pheromone(graph, tau0=0.1):
    pher = {}
    for u in _all_nodes():
        for v in _safe_neighbors(graph, u):
            pher[(u, v)] = tau0
    return pher


def _heuristic_cost(graph, u, v, W_delay, W_reliability, W_resource):
    # Heuristic = 1 / cost
    c = calculate_weighted_link_cost(graph, u, v, W_delay, W_reliability, W_resource)
    return 1.0 / (c + 1e-9)


def _choose_next_acs(graph, pheromone, current, visited,
                     W_delay, W_reliability, W_resource,
                     alpha, beta, q0):
    """
    ACS state transition rule:
    - with prob q0: choose argmax (tau^alpha * eta^beta)
    - else: roulette wheel
    """
    neighbors = [v for v in _safe_neighbors(graph, current) if v not in visited]
    if not neighbors:
        return None

    scored = []
    for v in neighbors:
        tau = pheromone.get((current, v), 1e-6)
        eta = _heuristic_cost(graph, current, v, W_delay, W_reliability, W_resource)
        value = (tau ** alpha) * (eta ** beta)
        scored.append((v, value))

    # Exploitation
    if random.random() < q0:
        return max(scored, key=lambda x: x[1])[0]

    # Exploration (roulette)
    total = sum(val for _, val in scored)
    r = random.random() * total
    acc = 0.0
    for v, val in scored:
        acc += val
        if acc >= r:
            return v
    return scored[-1][0]


def _local_update(pheromone, u, v, phi, tau0):
    """
    ACS local update:
    tau(u,v) = (1-phi)*tau(u,v) + phi*tau0
    """
    old = pheromone.get((u, v), tau0)
    pheromone[(u, v)] = (1.0 - phi) * old + phi * tau0


def _global_evaporate(pheromone, rho):
    for e in list(pheromone.keys()):
        pheromone[e] *= (1.0 - rho)


def _global_deposit_best(pheromone, best_path, best_cost, rho):
    """
    ACS global update (only best path):
    tau(u,v) = (1-rho)*tau(u,v) + rho*(1/best_cost)
    """
    delta = 1.0 / (best_cost + 1e-9)
    for i in range(len(best_path) - 1):
        e = (best_path[i], best_path[i + 1])
        pheromone[e] = (1.0 - rho) * pheromone.get(e, 0.0) + rho * delta


def _build_ant_path_acs(graph, pheromone, source, dest,
                        W_delay, W_reliability, W_resource,
                        alpha, beta, q0, phi, tau0,
                        max_steps=200):
    current = source
    visited = {current}
    path = [current]

    for _ in range(max_steps):
        if current == dest:
            return path

        nxt = _choose_next_acs(
            graph, pheromone, current, visited,
            W_delay, W_reliability, W_resource,
            alpha, beta, q0
        )
        if nxt is None:
            return None

        # Local pheromone update on used edge
        _local_update(pheromone, current, nxt, phi, tau0)

        path.append(nxt)
        visited.add(nxt)
        current = nxt

    return None


def run_aco(graph, source, dest, W_delay, W_reliability, W_resource, params=None):
    """
    ACO-Step3: ACS (Ant Colony System)
    """
    if params is None or not isinstance(params, dict):
            params = {}

    # Fast defaults 
    num_ants = int(params.get("num_ants", 20))
    num_iters = int(params.get("num_iters", 10))
    max_steps = int(params.get("max_steps", 200))

    alpha = float(params.get("alpha", 1.0))
    beta = float(params.get("beta", 2.0))

    rho = float(params.get("rho", 0.1))   # global evaporation/update
    phi = float(params.get("phi", 0.1))   # local update rate
    tau0 = float(params.get("tau0", 0.1))
    q0 = float(params.get("q0", 0.3))     # exploitation probability

    print(f"[ACS] Başlangıç: {source} → Hedef: {dest}")
    print(f"[ACS] ants={num_ants}, iters={num_iters}, q0={q0}, rho={rho}, phi={phi}, max_steps={max_steps}")

    pheromone = _init_pheromone(graph, tau0=tau0)

    best_path = None
    best_cost = float("inf")
    best_metrics = (None, None, None)

    for it in range(num_iters):
        iter_best_path = None
        iter_best_cost = float("inf")
        iter_best_metrics = (None, None, None)

        for _ in range(num_ants):
            path = _build_ant_path_acs(
                graph, pheromone, source, dest,
                W_delay, W_reliability, W_resource,
                alpha, beta, q0, phi, tau0,
                max_steps=max_steps
            )
            if not path:
                continue

            d, r, res, c = evaluate_path(graph, path, W_delay, W_reliability, W_resource)

            if c < iter_best_cost:
                iter_best_cost = c
                iter_best_path = path
                iter_best_metrics = (d, r, res)

            if c < best_cost:
                best_cost = c
                best_path = path
                best_metrics = (d, r, res)

        # Global pheromone update: evaporate + reinforce best path of iteration (or global best)
        _global_evaporate(pheromone, rho)
        if iter_best_path is not None:
            _global_deposit_best(pheromone, iter_best_path, iter_best_cost, rho)

        print(f"[ACS] Iter {it+1}/{num_iters} | best_cost={best_cost:.4f}")

    if best_path is None:
        return {
            "best_path": None,
            "total_delay": None,
            "total_reliability_cost": None,
            "total_resource_cost": None,
            "total_cost": None,
            "algo_name": "ACS",
            "note": "ACS yol bulamadı."
        }

    d, r, res = best_metrics
    return {
        "best_path": best_path,
        "total_delay": float(d),
        "total_reliability_cost": float(r),
        "total_resource_cost": float(res),
        "total_cost": float(best_cost),
        "algo_name": "ACS-step3",
        "note": "ACS (local+global pheromone update) çalıştırıldı."
    }
