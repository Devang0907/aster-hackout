INTERVENTIONS = {

    # =========================================================
    # ELECTRICITY
    # =========================================================

    "renewable_electricity": {
        "name": "Increase Renewable Electricity Usage",
        "source": "electricity",
        "category": "renewable_energy",

        "cost": 50000,
        "savings": 18000,

        "co2_reduction_rate": 0.28,
        "feasibility": 0.85,

        "implementation_time_months": 6,
        "maintenance_cost": 3000,
        "risk": 0.20,

        "description":
            "Increase the share of electricity supplied by renewable sources "
            "such as rooftop solar or renewable power procurement.",

        "requirements": [
            "Available roof or land area",
            "Suitable solar potential",
            "Grid or renewable electricity access"
        ]
    },

    "energy_efficiency": {
        "name": "Improve Energy Efficiency",
        "source": "electricity",
        "category": "energy_efficiency",

        "cost": 25000,
        "savings": 12000,

        "co2_reduction_rate": 0.18,
        "feasibility": 0.95,

        "implementation_time_months": 3,
        "maintenance_cost": 1500,
        "risk": 0.10,

        "description":
            "Reduce electricity consumption through efficient motors, "
            "LED lighting, optimized machinery and energy management.",

        "requirements": [
            "Energy consumption monitoring",
            "Equipment audit",
            "Access to inefficient equipment"
        ]
    },

    "smart_energy_management": {
        "name": "Deploy Smart Energy Management",
        "source": "electricity",
        "category": "energy_efficiency",

        "cost": 18000,
        "savings": 8500,

        "co2_reduction_rate": 0.12,
        "feasibility": 0.88,

        "implementation_time_months": 2,
        "maintenance_cost": 1000,
        "risk": 0.12,

        "description":
            "Use sensors, monitoring and automated controls to identify "
            "and reduce unnecessary electricity consumption.",

        "requirements": [
            "Energy meters",
            "IoT or monitoring infrastructure",
            "Basic digital monitoring"
        ]
    },

    # =========================================================
    # DIESEL / FUEL
    # =========================================================

    "fuel_efficiency": {
        "name": "Improve Fuel Efficiency",
        "source": "diesel",
        "category": "fuel_efficiency",

        "cost": 20000,
        "savings": 9000,

        "co2_reduction_rate": 0.20,
        "feasibility": 0.90,

        "implementation_time_months": 3,
        "maintenance_cost": 1800,
        "risk": 0.12,

        "description":
            "Reduce diesel consumption through equipment maintenance, "
            "operational optimization and fuel-efficient practices.",

        "requirements": [
            "Fuel consumption tracking",
            "Equipment inspection",
            "Operational monitoring"
        ]
    },

    "fuel_switching": {
        "name": "Switch to Lower-Carbon Fuel",
        "source": "diesel",
        "category": "fuel_transition",

        "cost": 45000,
        "savings": 14000,

        "co2_reduction_rate": 0.25,
        "feasibility": 0.70,

        "implementation_time_months": 8,
        "maintenance_cost": 3000,
        "risk": 0.25,

        "description":
            "Replace high-carbon fuel usage with a lower-carbon alternative "
            "where technically and economically feasible.",

        "requirements": [
            "Compatible equipment",
            "Alternative fuel availability",
            "Fuel infrastructure"
        ]
    },

    # =========================================================
    # RAW MATERIAL
    # =========================================================

    "recycled_material": {
        "name": "Increase Recycled Material Usage",
        "source": "raw_material",
        "category": "circular_material",

        "cost": 15000,
        "savings": 7000,

        "co2_reduction_rate": 0.20,
        "feasibility": 0.80,

        "implementation_time_months": 4,
        "maintenance_cost": 1200,
        "risk": 0.18,

        "description":
            "Replace a portion of virgin raw materials with suitable "
            "recycled or recovered materials.",

        "requirements": [
            "Reliable recycled material supplier",
            "Required material quality",
            "Production compatibility"
        ]
    },

    "material_efficiency": {
        "name": "Improve Material Efficiency",
        "source": "raw_material",
        "category": "material_efficiency",

        "cost": 20000,
        "savings": 9000,

        "co2_reduction_rate": 0.24,
        "feasibility": 0.85,

        "implementation_time_months": 5,
        "maintenance_cost": 1500,
        "risk": 0.15,

        "description":
            "Reduce raw material consumption through process optimization, "
            "better design and reduction of production losses.",

        "requirements": [
            "Material usage data",
            "Process analysis",
            "Production optimization"
        ]
    },

    "sustainable_material_substitution": {
        "name": "Substitute with Lower-Carbon Materials",
        "source": "raw_material",
        "category": "material_substitution",

        "cost": 30000,
        "savings": 10000,

        "co2_reduction_rate": 0.22,
        "feasibility": 0.72,

        "implementation_time_months": 7,
        "maintenance_cost": 2000,
        "risk": 0.25,

        "description":
            "Replace carbon-intensive virgin materials with lower-carbon "
            "or sustainably sourced alternatives.",

        "requirements": [
            "Alternative material supplier",
            "Quality validation",
            "Production compatibility"
        ]
    },

    # =========================================================
    # WASTE
    # =========================================================

    "waste_recovery": {
        "name": "Improve Waste Recovery",
        "source": "waste",
        "category": "waste_recovery",

        "cost": 10000,
        "savings": 3000,

        "co2_reduction_rate": 0.30,
        "feasibility": 0.85,

        "implementation_time_months": 3,
        "maintenance_cost": 1000,
        "risk": 0.10,

        "description":
            "Recover useful materials from industrial waste instead of "
            "sending them directly to disposal.",

        "requirements": [
            "Waste segregation",
            "Recovery facility or partner",
            "Waste tracking"
        ]
    },

    "waste_recycling": {
        "name": "Increase Waste Recycling",
        "source": "waste",
        "category": "recycling",

        "cost": 14000,
        "savings": 4500,

        "co2_reduction_rate": 0.25,
        "feasibility": 0.88,

        "implementation_time_months": 4,
        "maintenance_cost": 1200,
        "risk": 0.12,

        "description":
            "Improve segregation and recycling of production waste "
            "to reduce disposal and virgin material demand.",

        "requirements": [
            "Waste segregation system",
            "Recycling partner",
            "Employee participation"
        ]
    },

    "industrial_symbiosis": {
        "name": "Industrial Waste Exchange",
        "source": "waste",
        "category": "industrial_symbiosis",

        "cost": 12000,
        "savings": 6000,

        "co2_reduction_rate": 0.35,
        "feasibility": 0.65,

        "implementation_time_months": 9,
        "maintenance_cost": 1500,
        "risk": 0.30,

        "description":
            "Identify opportunities where one company's waste stream "
            "can become another company's useful input.",

        "requirements": [
            "Nearby industrial partners",
            "Compatible waste streams",
            "Logistics coordination"
        ]
    },

    # =========================================================
    # TRANSPORT
    # =========================================================

    "transport_optimization": {
        "name": "Optimize Transportation",
        "source": "transport",
        "category": "logistics",

        "cost": 12000,
        "savings": 5000,

        "co2_reduction_rate": 0.16,
        "feasibility": 0.75,

        "implementation_time_months": 3,
        "maintenance_cost": 1000,
        "risk": 0.15,

        "description":
            "Reduce transportation emissions through route optimization, "
            "load consolidation and better logistics planning.",

        "requirements": [
            "Transport data",
            "Delivery schedules",
            "Route information"
        ]
    },

    "electric_transport": {
        "name": "Transition to Electric Transport",
        "source": "transport",
        "category": "transport_transition",

        "cost": 60000,
        "savings": 15000,

        "co2_reduction_rate": 0.30,
        "feasibility": 0.60,

        "implementation_time_months": 12,
        "maintenance_cost": 2500,
        "risk": 0.30,

        "description":
            "Replace suitable fossil-fuel transportation vehicles with "
            "electric alternatives.",

        "requirements": [
            "Charging infrastructure",
            "Suitable vehicle availability",
            "Electricity access"
        ]
    }
}