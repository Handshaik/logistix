from rules import generate_driver_rules, generate_packages, RULE_TEMPLATES


def main():
    driver_ids = [f"driver_{i}" for i in range(1, 100)]
    drivers = generate_driver_rules(driver_ids, RULE_TEMPLATES, min_rules=0, max_rules=2)
    packages = generate_packages(len(drivers) * 10, RULE_TEMPLATES)

    for package in packages:
        print(package.id)



if __name__ == "__main__":
    main()
