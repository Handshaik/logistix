import random
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Driver:
    id: str
    rules: List[Dict[str, Any]]

RULE_TEMPLATES: List[Dict[str, Any]] = [
    {"code": "MAX_WEIGHT",     "params": {"limit_kg": 10}},
    {"code": "NO_PERISHABLE",  "params": {}},
    {"code": "REGION_ONLY",    "params": {"allowed_regions": ["north","east","south","west"]}},
    {"code": "MAX_DISTANCE",   "params": {"max_km": 50}},
    {"code": "EXPRESS_ONLY",   "params": {}},
    {"code": "FRAGILE_ONLY",   "params": {}},
    {"code": "HAZMAT_ALLOWED", "params": {"allowed_classes": [1,2,3,4]}},
    {"code": "TEMP_CONTROL",   "params": {"min_c": 2, "max_c": 8}},
    {"code": "TIME_WINDOW",    "params": {"start_hour": 8, "end_hour": 17}},
    {"code": "OVERSIZED",      "params": {"min_volume_m3": 0.5}},
]

def generate_driver_rules(
    driver_ids: List[str],
    rule_templates: List[Dict[str, Any]],
    min_rules: int = 2,
    max_rules: int = 4,
    seed: int = None,
) -> List[Driver]:
    if seed is not None:
        random.seed(seed)

    drivers: List[Driver] = []
    for driver_id in driver_ids:
        k = random.randint(min_rules, max_rules)
        chosen = random.sample(rule_templates, k)
        instantiated: List[Dict[str, Any]] = []
        for tmpl in chosen:
            params = tmpl["params"].copy()
            # Customize list-based params
            if tmpl["code"] == "REGION_ONLY":
                regions = params["allowed_regions"]
                params["allowed_regions"] = random.sample(regions, k=2)
            if tmpl["code"] == "HAZMAT_ALLOWED":
                classes = params["allowed_classes"]
                params["allowed_classes"] = random.sample(classes, k=random.randint(1,2))
            instantiated.append({
                "rule_id": str(uuid.uuid4()),
                "code": tmpl["code"],
                "params": params
            })
        drivers.append(Driver(id=driver_id, rules=instantiated))
    return drivers


def generate_packages(
    num_packages: int,
    rule_templates: List[Dict[str, Any]],
    seed: int = None,
) -> List[Dict[str, Any]]:
    
    if seed is not None:
        random.seed(seed + 1)

    # Extract static domains for region & hazmat
    regions = next(r for r in rule_templates if r["code"]=="REGION_ONLY")["params"]["allowed_regions"]
    hazmat_classes = next(r for r in rule_templates if r["code"]=="HAZMAT_ALLOWED")["params"]["allowed_classes"]
    
    packages = []
    for _ in range(num_packages):
        pkg = {
            "package_id": str(uuid.uuid4()),
            "weight_kg": round(random.uniform(0.5, 20), 2),
            "is_perishable": random.choice([True, False]),
            "region": random.choice(regions),
            "distance_km": round(random.uniform(1, 100), 2),
            "is_express": random.choice([True, False]),
            "is_fragile": random.choice([True, False]),
            "hazmat_class": random.choice(hazmat_classes + [None]),
            "temperature_c": round(random.uniform(-5, 25), 2),
            "delivery_hour": random.randint(0, 23),
            "volume_m3": round(random.uniform(0.1, 3.0), 2)
        }
        packages.append(pkg)
    return packages

if __name__ == "__main__":
    driver_ids = [f"driver_{i}" for i in range(1, 100)]
    drivers = generate_driver_rules(driver_ids, RULE_TEMPLATES, min_rules=0, max_rules=2)
    packages = generate_packages(len(drivers) * 10, RULE_TEMPLATES)

    print("Sample driver assignments:")
    print(drivers[:3])
    print("Sample packages:")
    print(packages[:3])

