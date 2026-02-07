"""
PC Builds Catalog - 7 Tiers from Scrapper to UNLIMITED POWER!
==============================================================

Complete PC build configurations for every budget level.
Designed for integration with Shopify connector for automated store listings.

Prices reflect December 2024/January 2025 market rates.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json


class BuildTier(Enum):
    """PC Build tier classifications"""
    SCRAPPER = "scrapper"           # $0-200
    BUDGET_WARRIOR = "budget"       # $400-600
    SOLID_PERFORMER = "mid"         # $900-1200
    POWER_PLAYER = "high"           # $1800-2500
    BEAST = "enthusiast"            # $3500-5000
    TITAN = "extreme"               # $7000-10000
    UNLIMITED_POWER = "unlimited"   # $15000-25000+


@dataclass
class Component:
    """Individual PC component"""
    category: str
    name: str
    model: str
    price: float
    specs: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class PCBuild:
    """Complete PC build configuration"""
    tier: BuildTier
    name: str
    tagline: str
    description: str
    price_range: str
    target_audience: List[str]
    use_cases: List[str]
    performance_notes: List[str]
    components: List[Component]
    total_price: float = 0.0

    def __post_init__(self):
        self.total_price = sum(c.price for c in self.components)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier.value,
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "price_range": self.price_range,
            "target_audience": self.target_audience,
            "use_cases": self.use_cases,
            "performance_notes": self.performance_notes,
            "total_price": self.total_price,
            "components": [
                {
                    "category": c.category,
                    "name": c.name,
                    "model": c.model,
                    "price": c.price,
                    "specs": c.specs,
                    "notes": c.notes
                }
                for c in self.components
            ]
        }


# =============================================================================
# TIER 1: THE SCRAPPER ($0-200)
# =============================================================================

TIER_1_SCRAPPER = PCBuild(
    tier=BuildTier.SCRAPPER,
    name="The Scrapper",
    tagline="From the ashes, a PC rises",
    description="""
    Built from salvaged, used, and refurbished parts. Perfect for those starting
    with nothing but determination. Focuses on reliability over performance.
    Hunt for deals on eBay, Facebook Marketplace, and local recycling centers.
    """,
    price_range="$0 - $200",
    target_audience=[
        "Students on extreme budgets",
        "First-time builders learning the ropes",
        "Basic home office users",
        "Retro gaming enthusiasts"
    ],
    use_cases=[
        "Web browsing and email",
        "Document editing (Word, Excel)",
        "YouTube and streaming video",
        "Retro/indie gaming",
        "Learning Linux"
    ],
    performance_notes=[
        "Can handle 720p-1080p video playback",
        "Light multitasking (3-5 browser tabs)",
        "Older games (pre-2015) playable",
        "Not suitable for modern gaming or content creation"
    ],
    components=[
        Component(
            category="CPU",
            name="Intel Core i5-4590",
            model="Used/Pulled from office PC",
            price=25.00,
            specs={
                "cores": 4,
                "threads": 4,
                "base_clock": "3.3 GHz",
                "boost_clock": "3.7 GHz",
                "tdp": "84W",
                "generation": "Haswell (4th Gen)"
            },
            notes="Pulled from retired office systems, still capable for basic tasks"
        ),
        Component(
            category="GPU",
            name="NVIDIA GTX 750 Ti",
            model="Used",
            price=35.00,
            specs={
                "vram": "2GB GDDR5",
                "cuda_cores": 640,
                "memory_bus": "128-bit",
                "tdp": "60W"
            },
            notes="No external power needed, great for budget builds"
        ),
        Component(
            category="RAM",
            name="Generic DDR3 1600MHz",
            model="8GB (2x4GB) Used",
            price=15.00,
            specs={
                "capacity": "8GB",
                "speed": "1600MHz",
                "type": "DDR3",
                "channels": "Dual"
            },
            notes="Salvaged from office PCs"
        ),
        Component(
            category="Storage",
            name="Mixed HDD + SSD",
            model="120GB SSD + 500GB HDD (Used)",
            price=25.00,
            specs={
                "ssd_capacity": "120GB",
                "hdd_capacity": "500GB",
                "ssd_interface": "SATA III",
                "hdd_rpm": "7200"
            },
            notes="SSD for OS, HDD for storage"
        ),
        Component(
            category="Motherboard",
            name="Generic LGA 1150 Board",
            model="Dell/HP/Lenovo OEM (Used)",
            price=30.00,
            specs={
                "socket": "LGA 1150",
                "chipset": "H81/B85",
                "ram_slots": 2,
                "max_ram": "16GB"
            },
            notes="Pulled from office systems, may need case adapter"
        ),
        Component(
            category="PSU",
            name="Generic 400W",
            model="Used/Refurbished",
            price=20.00,
            specs={
                "wattage": "400W",
                "efficiency": "80+",
                "modular": False
            },
            notes="Test before use, ensure all cables present"
        ),
        Component(
            category="Case",
            name="Salvaged Mid-Tower",
            model="Any functional case",
            price=0.00,
            specs={
                "form_factor": "ATX Mid-Tower",
                "front_io": "Varies"
            },
            notes="Free from recycling center or friend's old build"
        ),
        Component(
            category="Cooling",
            name="Stock Intel Cooler",
            model="Included with CPU",
            price=0.00,
            specs={
                "type": "Air",
                "noise_level": "Moderate"
            },
            notes="Adequate for stock speeds"
        )
    ]
)


# =============================================================================
# TIER 2: THE BUDGET WARRIOR ($400-600)
# =============================================================================

TIER_2_BUDGET_WARRIOR = PCBuild(
    tier=BuildTier.BUDGET_WARRIOR,
    name="The Budget Warrior",
    tagline="Small budget, big dreams",
    description="""
    The entry point for real PC gaming. New parts with warranty protection.
    Capable of 1080p gaming at low-medium settings in modern titles.
    Best bang-for-buck components prioritized.
    """,
    price_range="$400 - $600",
    target_audience=[
        "First-time PC gamers",
        "Console converts",
        "Students needing gaming + productivity",
        "Casual gamers"
    ],
    use_cases=[
        "1080p gaming at 30-60 FPS (low-medium)",
        "E-sports titles at 60+ FPS",
        "Streaming video in 4K",
        "Light content creation",
        "Programming and web development"
    ],
    performance_notes=[
        "Fortnite, Valorant, CS2 at 60+ FPS",
        "AAA games at 30-45 FPS low-medium",
        "Smooth 1080p desktop experience",
        "Can handle light video editing"
    ],
    components=[
        Component(
            category="CPU",
            name="AMD Ryzen 5 5600",
            model="100-100000927BOX",
            price=129.00,
            specs={
                "cores": 6,
                "threads": 12,
                "base_clock": "3.5 GHz",
                "boost_clock": "4.4 GHz",
                "tdp": "65W",
                "architecture": "Zen 3"
            },
            notes="Best budget gaming CPU, excellent single-thread performance"
        ),
        Component(
            category="GPU",
            name="AMD Radeon RX 6600",
            model="8GB GDDR6",
            price=189.00,
            specs={
                "vram": "8GB GDDR6",
                "stream_processors": 1792,
                "memory_bus": "128-bit",
                "tdp": "132W",
                "ray_tracing": True
            },
            notes="Great 1080p performance, excellent efficiency"
        ),
        Component(
            category="RAM",
            name="G.Skill Ripjaws V",
            model="16GB (2x8GB) DDR4-3200",
            price=42.00,
            specs={
                "capacity": "16GB",
                "speed": "3200MHz",
                "type": "DDR4",
                "cas_latency": "CL16",
                "voltage": "1.35V"
            },
            notes="Sweet spot for Ryzen performance"
        ),
        Component(
            category="Storage",
            name="Kingston NV2",
            model="500GB NVMe SSD",
            price=35.00,
            specs={
                "capacity": "500GB",
                "interface": "NVMe PCIe 4.0",
                "read_speed": "3500 MB/s",
                "write_speed": "2100 MB/s"
            },
            notes="Fast boot and game loads, add HDD later for more storage"
        ),
        Component(
            category="Motherboard",
            name="MSI B550M PRO-VDH WiFi",
            model="Micro-ATX",
            price=99.00,
            specs={
                "socket": "AM4",
                "chipset": "B550",
                "ram_slots": 4,
                "max_ram": "128GB",
                "wifi": "WiFi 6",
                "pcie_slots": "1x PCIe 4.0 x16"
            },
            notes="Great budget board with WiFi included"
        ),
        Component(
            category="PSU",
            name="EVGA 500 GD",
            model="500W 80+ Gold",
            price=49.00,
            specs={
                "wattage": "500W",
                "efficiency": "80+ Gold",
                "modular": False,
                "warranty": "5 years"
            },
            notes="Reliable budget PSU with good efficiency"
        ),
        Component(
            category="Case",
            name="Thermaltake Versa H18",
            model="Micro-ATX",
            price=49.00,
            specs={
                "form_factor": "Micro-ATX",
                "tempered_glass": True,
                "included_fans": 1,
                "gpu_clearance": "350mm"
            },
            notes="Clean budget case with good airflow"
        ),
        Component(
            category="Cooling",
            name="AMD Wraith Stealth",
            model="Included with CPU",
            price=0.00,
            specs={
                "type": "Air",
                "height": "54mm",
                "noise_level": "Quiet"
            },
            notes="Stock cooler is adequate for R5 5600"
        )
    ]
)


# =============================================================================
# TIER 3: THE SOLID PERFORMER ($900-1200)
# =============================================================================

TIER_3_SOLID_PERFORMER = PCBuild(
    tier=BuildTier.SOLID_PERFORMER,
    name="The Solid Performer",
    tagline="The sweet spot of PC gaming",
    description="""
    The recommended build for most gamers. Excellent 1080p performance with
    high/ultra settings, entry-level 1440p capability. Great for content
    creation, streaming, and productivity.
    """,
    price_range="$900 - $1,200",
    target_audience=[
        "Dedicated PC gamers",
        "Streamers starting out",
        "Content creators (YouTube, TikTok)",
        "Developers and programmers",
        "Work-from-home professionals"
    ],
    use_cases=[
        "1080p Ultra gaming at 100+ FPS",
        "1440p gaming at 60+ FPS",
        "Game streaming at 1080p",
        "Video editing (1080p-4K)",
        "3D modeling (hobbyist)",
        "Software development with multiple monitors"
    ],
    performance_notes=[
        "Cyberpunk 2077 at 1080p High: 70+ FPS",
        "E-sports titles: 200+ FPS",
        "Premiere Pro timeline scrubbing: Smooth",
        "Multitasking beast with 32GB RAM option"
    ],
    components=[
        Component(
            category="CPU",
            name="AMD Ryzen 5 7600X",
            model="100-100000593WOF",
            price=199.00,
            specs={
                "cores": 6,
                "threads": 12,
                "base_clock": "4.7 GHz",
                "boost_clock": "5.3 GHz",
                "tdp": "105W",
                "architecture": "Zen 4"
            },
            notes="Latest gen, excellent gaming and productivity"
        ),
        Component(
            category="GPU",
            name="NVIDIA GeForce RTX 4060 Ti",
            model="8GB GDDR6",
            price=379.00,
            specs={
                "vram": "8GB GDDR6",
                "cuda_cores": 4352,
                "memory_bus": "128-bit",
                "tdp": "160W",
                "ray_tracing": True,
                "dlss": "DLSS 3.0"
            },
            notes="Great 1080p-1440p GPU with DLSS 3 Frame Generation"
        ),
        Component(
            category="RAM",
            name="G.Skill Flare X5",
            model="32GB (2x16GB) DDR5-6000",
            price=109.00,
            specs={
                "capacity": "32GB",
                "speed": "6000MHz",
                "type": "DDR5",
                "cas_latency": "CL36",
                "expo": True
            },
            notes="Optimized for AMD EXPO, future-proof capacity"
        ),
        Component(
            category="Storage",
            name="WD Black SN770",
            model="1TB NVMe SSD",
            price=79.00,
            specs={
                "capacity": "1TB",
                "interface": "NVMe PCIe 4.0",
                "read_speed": "5150 MB/s",
                "write_speed": "4900 MB/s"
            },
            notes="Excellent performance for the price"
        ),
        Component(
            category="Motherboard",
            name="MSI MAG B650 TOMAHAWK WiFi",
            model="ATX",
            price=189.00,
            specs={
                "socket": "AM5",
                "chipset": "B650",
                "ram_slots": 4,
                "max_ram": "128GB",
                "wifi": "WiFi 6E",
                "pcie_slots": "1x PCIe 5.0 x16",
                "m2_slots": 2
            },
            notes="Solid mid-range board with great VRMs"
        ),
        Component(
            category="PSU",
            name="Corsair RM650",
            model="650W 80+ Gold",
            price=89.00,
            specs={
                "wattage": "650W",
                "efficiency": "80+ Gold",
                "modular": True,
                "warranty": "10 years"
            },
            notes="Reliable, fully modular, excellent warranty"
        ),
        Component(
            category="Case",
            name="Fractal Design Pop Air",
            model="ATX Mid-Tower",
            price=89.00,
            specs={
                "form_factor": "ATX",
                "tempered_glass": True,
                "included_fans": 3,
                "gpu_clearance": "405mm",
                "airflow_focused": True
            },
            notes="Excellent airflow case with mesh front"
        ),
        Component(
            category="Cooling",
            name="Thermalright Peerless Assassin 120 SE",
            model="Dual Tower Air Cooler",
            price=35.00,
            specs={
                "type": "Air",
                "height": "155mm",
                "fans": 2,
                "tdp_rating": "260W",
                "noise_level": "Very Quiet"
            },
            notes="Incredible value, competes with $80+ coolers"
        )
    ]
)


# =============================================================================
# TIER 4: THE POWER PLAYER ($1800-2500)
# =============================================================================

TIER_4_POWER_PLAYER = PCBuild(
    tier=BuildTier.POWER_PLAYER,
    name="The Power Player",
    tagline="Where performance meets ambition",
    description="""
    High-end gaming and content creation powerhouse. Excellent 1440p Ultra
    performance, capable 4K gaming. Professional-grade productivity with
    premium components and aesthetics.
    """,
    price_range="$1,800 - $2,500",
    target_audience=[
        "Serious gamers with demanding titles",
        "Professional streamers",
        "Content creators (YouTube, Twitch)",
        "Video editors (4K workflows)",
        "3D artists and designers",
        "Software developers with heavy workloads"
    ],
    use_cases=[
        "1440p Ultra gaming at 120+ FPS",
        "4K gaming at 60+ FPS",
        "Professional streaming at 1080p/1440p",
        "4K video editing with minimal proxy",
        "3D rendering (Blender, Cinema 4D)",
        "AI/ML experimentation",
        "Virtual Reality (VR)"
    ],
    performance_notes=[
        "Cyberpunk 2077 4K DLSS Quality: 80+ FPS",
        "1440p competitive: 200+ FPS",
        "DaVinci Resolve 4K timeline: Real-time",
        "Blender Cycles rendering: GPU accelerated"
    ],
    components=[
        Component(
            category="CPU",
            name="AMD Ryzen 7 7800X3D",
            model="100-100000910WOF",
            price=339.00,
            specs={
                "cores": 8,
                "threads": 16,
                "base_clock": "4.2 GHz",
                "boost_clock": "5.0 GHz",
                "l3_cache": "96MB (3D V-Cache)",
                "tdp": "120W",
                "architecture": "Zen 4 + 3D V-Cache"
            },
            notes="Best gaming CPU on the market, incredible 3D V-Cache"
        ),
        Component(
            category="GPU",
            name="NVIDIA GeForce RTX 4070 Ti SUPER",
            model="16GB GDDR6X",
            price=799.00,
            specs={
                "vram": "16GB GDDR6X",
                "cuda_cores": 8448,
                "memory_bus": "256-bit",
                "tdp": "285W",
                "ray_tracing": True,
                "dlss": "DLSS 3.0"
            },
            notes="Excellent 1440p-4K GPU with 16GB for future-proofing"
        ),
        Component(
            category="RAM",
            name="G.Skill Trident Z5 RGB",
            model="64GB (2x32GB) DDR5-6400",
            price=199.00,
            specs={
                "capacity": "64GB",
                "speed": "6400MHz",
                "type": "DDR5",
                "cas_latency": "CL32",
                "rgb": True,
                "expo": True
            },
            notes="Premium RGB RAM with excellent timings"
        ),
        Component(
            category="Storage",
            name="Samsung 990 Pro",
            model="2TB NVMe SSD",
            price=179.00,
            specs={
                "capacity": "2TB",
                "interface": "NVMe PCIe 4.0",
                "read_speed": "7450 MB/s",
                "write_speed": "6900 MB/s",
                "endurance": "1200 TBW"
            },
            notes="Top-tier Gen4 SSD, excellent for game loading"
        ),
        Component(
            category="Storage Secondary",
            name="Seagate Barracuda",
            model="4TB HDD",
            price=79.00,
            specs={
                "capacity": "4TB",
                "rpm": 5400,
                "cache": "256MB",
                "interface": "SATA III"
            },
            notes="Mass storage for games and media"
        ),
        Component(
            category="Motherboard",
            name="ASUS ROG STRIX B650E-E Gaming WiFi",
            model="ATX",
            price=299.00,
            specs={
                "socket": "AM5",
                "chipset": "B650E",
                "ram_slots": 4,
                "max_ram": "128GB DDR5",
                "wifi": "WiFi 6E",
                "pcie_slots": "1x PCIe 5.0 x16",
                "m2_slots": 4,
                "usb4": True
            },
            notes="Premium B650 with PCIe 5.0 and USB4"
        ),
        Component(
            category="PSU",
            name="Corsair RM850x",
            model="850W 80+ Gold",
            price=139.00,
            specs={
                "wattage": "850W",
                "efficiency": "80+ Gold",
                "modular": True,
                "warranty": "10 years",
                "atx3": True
            },
            notes="Excellent PSU with ATX 3.0 support"
        ),
        Component(
            category="Case",
            name="Lian Li Lancool II Mesh C",
            model="ATX Mid-Tower",
            price=119.00,
            specs={
                "form_factor": "ATX",
                "tempered_glass": True,
                "included_fans": 3,
                "gpu_clearance": "384mm",
                "cable_management": "Excellent"
            },
            notes="Top-tier airflow with premium build quality"
        ),
        Component(
            category="Cooling",
            name="Deepcool AK620 Digital",
            model="Dual Tower with LCD",
            price=79.00,
            specs={
                "type": "Air",
                "height": "160mm",
                "fans": 2,
                "tdp_rating": "260W",
                "display": "LCD Status Screen"
            },
            notes="Excellent cooling with fun LCD display"
        )
    ]
)


# =============================================================================
# TIER 5: THE BEAST ($3500-5000)
# =============================================================================

TIER_5_BEAST = PCBuild(
    tier=BuildTier.BEAST,
    name="The Beast",
    tagline="Uncompromising performance",
    description="""
    Enthusiast-grade system for those who demand the best. Native 4K gaming,
    professional content creation, AI/ML development, and LLM training
    capability. No compromises.
    """,
    price_range="$3,500 - $5,000",
    target_audience=[
        "Enthusiast gamers (4K 120Hz+)",
        "Professional content creators",
        "AI/ML developers",
        "LLM fine-tuning practitioners",
        "VFX artists",
        "Game developers",
        "Scientific computing users"
    ],
    use_cases=[
        "4K Ultra gaming at 100+ FPS",
        "8K video editing",
        "AI model training (Stable Diffusion, LLMs)",
        "Professional 3D rendering",
        "Multiple 4K monitor workstation",
        "VR development and gaming",
        "Large-scale simulations"
    ],
    performance_notes=[
        "RTX 4090: 95+ FPS in any game at 4K Ultra",
        "LLM inference: Run 13B-70B models locally",
        "Stable Diffusion: 2-3 second generation",
        "Blender: Real-time viewport rendering"
    ],
    components=[
        Component(
            category="CPU",
            name="AMD Ryzen 9 7950X3D",
            model="100-100000908WOF",
            price=549.00,
            specs={
                "cores": 16,
                "threads": 32,
                "base_clock": "4.2 GHz",
                "boost_clock": "5.7 GHz",
                "l3_cache": "128MB (64MB 3D V-Cache)",
                "tdp": "120W",
                "architecture": "Zen 4 + 3D V-Cache"
            },
            notes="Best of both worlds: gaming and productivity king"
        ),
        Component(
            category="GPU",
            name="NVIDIA GeForce RTX 4090",
            model="24GB GDDR6X",
            price=1899.00,
            specs={
                "vram": "24GB GDDR6X",
                "cuda_cores": 16384,
                "tensor_cores": 512,
                "memory_bus": "384-bit",
                "memory_bandwidth": "1008 GB/s",
                "tdp": "450W",
                "ray_tracing": True,
                "dlss": "DLSS 3.0"
            },
            notes="The ultimate GPU - nothing comes close"
        ),
        Component(
            category="RAM",
            name="G.Skill Trident Z5 Royal",
            model="128GB (4x32GB) DDR5-6000",
            price=399.00,
            specs={
                "capacity": "128GB",
                "speed": "6000MHz",
                "type": "DDR5",
                "cas_latency": "CL30",
                "rgb": True,
                "heat_spreader": "Premium"
            },
            notes="Massive capacity for AI/ML workloads"
        ),
        Component(
            category="Storage Primary",
            name="Samsung 990 Pro",
            model="4TB NVMe SSD",
            price=329.00,
            specs={
                "capacity": "4TB",
                "interface": "NVMe PCIe 4.0",
                "read_speed": "7450 MB/s",
                "write_speed": "6900 MB/s",
                "endurance": "2400 TBW"
            },
            notes="Primary OS and active projects"
        ),
        Component(
            category="Storage Secondary",
            name="Crucial T700",
            model="2TB NVMe PCIe 5.0",
            price=279.00,
            specs={
                "capacity": "2TB",
                "interface": "NVMe PCIe 5.0",
                "read_speed": "12400 MB/s",
                "write_speed": "11800 MB/s"
            },
            notes="Fastest consumer SSD for scratch disk"
        ),
        Component(
            category="Storage Tertiary",
            name="Seagate IronWolf Pro",
            model="8TB NAS HDD",
            price=189.00,
            specs={
                "capacity": "8TB",
                "rpm": 7200,
                "cache": "256MB",
                "workload_rate": "300TB/year"
            },
            notes="High-endurance mass storage"
        ),
        Component(
            category="Motherboard",
            name="ASUS ROG Crosshair X670E Hero",
            model="ATX",
            price=499.00,
            specs={
                "socket": "AM5",
                "chipset": "X670E",
                "ram_slots": 4,
                "max_ram": "128GB DDR5",
                "wifi": "WiFi 6E",
                "pcie_slots": "2x PCIe 5.0 x16",
                "m2_slots": 5,
                "usb4": True,
                "thunderbolt4": True
            },
            notes="Premium flagship board with every feature"
        ),
        Component(
            category="PSU",
            name="Corsair AX1000",
            model="1000W 80+ Titanium",
            price=299.00,
            specs={
                "wattage": "1000W",
                "efficiency": "80+ Titanium",
                "modular": True,
                "warranty": "10 years",
                "atx3": True
            },
            notes="Titanium efficiency for 24/7 operation"
        ),
        Component(
            category="Case",
            name="Fractal Design Torrent",
            model="ATX Full Tower",
            price=229.00,
            specs={
                "form_factor": "E-ATX",
                "tempered_glass": True,
                "included_fans": "2x 180mm + 3x 140mm",
                "gpu_clearance": "461mm",
                "airflow_focused": True
            },
            notes="Best-in-class airflow for high-TDP components"
        ),
        Component(
            category="Cooling",
            name="NZXT Kraken Z73",
            model="360mm AIO",
            price=249.00,
            specs={
                "type": "AIO Liquid",
                "radiator": "360mm",
                "fans": "3x 120mm",
                "pump": "7th Gen Asetek",
                "display": "2.36\" LCD"
            },
            notes="Premium AIO with customizable LCD display"
        )
    ]
)


# =============================================================================
# TIER 6: THE TITAN ($7000-10000)
# =============================================================================

TIER_6_TITAN = PCBuild(
    tier=BuildTier.TITAN,
    name="The Titan",
    tagline="When excellence is the only option",
    description="""
    Extreme enthusiast build pushing the boundaries of consumer hardware.
    Custom loop cooling, extreme overclocking potential, and professional
    workstation capabilities. Built for those who demand perfection.
    """,
    price_range="$7,000 - $10,000",
    target_audience=[
        "Extreme overclockers",
        "Professional studios",
        "AI/ML research teams",
        "8K content creators",
        "Competitive esports professionals",
        "Simulation engineers"
    ],
    use_cases=[
        "8K video editing and color grading",
        "Large language model training",
        "Real-time ray tracing development",
        "Professional VFX (Houdini, Maya)",
        "Multiple GPU workloads",
        "Extreme overclocking competitions",
        "24/7 rendering farm node"
    ],
    performance_notes=[
        "4K 240Hz gaming achievable",
        "8K 60 FPS with DLSS",
        "70B parameter LLM inference",
        "Dual GPU: 2x rendering performance",
        "Custom loop: 10-15C lower temps"
    ],
    components=[
        Component(
            category="CPU",
            name="Intel Core i9-14900KS",
            model="Special Edition",
            price=699.00,
            specs={
                "cores": 24,
                "threads": 32,
                "p_cores": "8 @ 6.2 GHz",
                "e_cores": "16 @ 4.5 GHz",
                "l3_cache": "36MB",
                "tdp": "150W (253W PL2)",
                "architecture": "Raptor Lake Refresh"
            },
            notes="Highest clocked consumer CPU ever made"
        ),
        Component(
            category="GPU Primary",
            name="NVIDIA GeForce RTX 4090",
            model="ASUS ROG STRIX OC 24GB",
            price=2199.00,
            specs={
                "vram": "24GB GDDR6X",
                "cuda_cores": 16384,
                "boost_clock": "2640 MHz (OC)",
                "memory_bus": "384-bit",
                "tdp": "450W",
                "cooling": "3.5-slot"
            },
            notes="Premium AIB card with best cooling"
        ),
        Component(
            category="GPU Secondary",
            name="NVIDIA GeForce RTX 4090",
            model="ASUS ROG STRIX OC 24GB",
            price=2199.00,
            specs={
                "vram": "24GB GDDR6X",
                "cuda_cores": 16384,
                "purpose": "NVLink rendering / AI training"
            },
            notes="Second GPU for multi-GPU workloads (no SLI - compute only)"
        ),
        Component(
            category="RAM",
            name="G.Skill Trident Z5 RGB",
            model="192GB (4x48GB) DDR5-6400",
            price=699.00,
            specs={
                "capacity": "192GB",
                "speed": "6400MHz",
                "type": "DDR5",
                "cas_latency": "CL32",
                "rgb": True
            },
            notes="Maximum capacity for extreme workloads"
        ),
        Component(
            category="Storage Primary",
            name="Crucial T700 w/Heatsink",
            model="4TB NVMe PCIe 5.0",
            price=499.00,
            specs={
                "capacity": "4TB",
                "interface": "NVMe PCIe 5.0",
                "read_speed": "12400 MB/s",
                "write_speed": "11800 MB/s"
            },
            notes="Fastest consumer storage available"
        ),
        Component(
            category="Storage Secondary",
            name="Samsung 990 Pro",
            model="4TB NVMe SSD x2",
            price=658.00,
            specs={
                "capacity": "8TB total (2x4TB)",
                "configuration": "RAID 0 optional",
                "read_speed": "7450 MB/s each"
            },
            notes="Project and asset storage"
        ),
        Component(
            category="Storage Tertiary",
            name="Seagate Exos X20",
            model="20TB Enterprise HDD",
            price=329.00,
            specs={
                "capacity": "20TB",
                "rpm": 7200,
                "cache": "256MB",
                "mtbf": "2.5M hours"
            },
            notes="Enterprise-grade archive storage"
        ),
        Component(
            category="Motherboard",
            name="ASUS ROG Maximus Z790 Extreme",
            model="E-ATX",
            price=799.00,
            specs={
                "socket": "LGA 1700",
                "chipset": "Z790",
                "ram_slots": 4,
                "max_ram": "192GB DDR5",
                "wifi": "WiFi 7",
                "pcie_slots": "2x PCIe 5.0 x16",
                "m2_slots": 5,
                "thunderbolt4": True,
                "power_stages": "24+1"
            },
            notes="Flagship board for extreme overclocking"
        ),
        Component(
            category="PSU",
            name="Corsair AX1600i",
            model="1600W 80+ Titanium",
            price=549.00,
            specs={
                "wattage": "1600W",
                "efficiency": "80+ Titanium",
                "modular": True,
                "digital_control": True,
                "warranty": "10 years"
            },
            notes="Powers dual 4090s with headroom to spare"
        ),
        Component(
            category="Case",
            name="Phanteks Enthoo 719",
            model="Full Tower",
            price=189.00,
            specs={
                "form_factor": "E-ATX",
                "tempered_glass": "Dual",
                "drive_bays": "12x 3.5\"",
                "gpu_clearance": "503mm",
                "dual_system": True
            },
            notes="Massive case for custom loops and dual GPUs"
        ),
        Component(
            category="Cooling",
            name="Custom Loop - EK Premium",
            model="Full CPU + Dual GPU",
            price=1499.00,
            specs={
                "type": "Custom Hard Tube",
                "radiators": "2x 480mm",
                "cpu_block": "EK-Quantum Velocity²",
                "gpu_blocks": "2x EK-Quantum Vector",
                "pump": "EK-Quantum Kinetic D5",
                "reservoir": "EK-Quantum Kinetic",
                "fittings": "Nickel",
                "coolant": "EK-CryoFuel"
            },
            notes="Premium custom loop for maximum cooling"
        )
    ]
)


# =============================================================================
# TIER 7: UNLIMITED POWER! ($15000-25000+)
# =============================================================================

TIER_7_UNLIMITED_POWER = PCBuild(
    tier=BuildTier.UNLIMITED_POWER,
    name="UNLIMITED POWER!",
    tagline="The dark side of PC building... is a pathway to many abilities some consider to be unnatural",
    description="""
    UNLIMITED POWER! When money is no object and only absolute supremacy will do.
    Threadripper PRO, dual flagship GPUs, 256GB+ RAM, custom everything.
    This is the Death Star of PCs - a fully armed and operational battlestation.

    "I have waited a long time for this, my little desktop friend."
    """,
    price_range="$15,000 - $25,000+",
    target_audience=[
        "Hollywood VFX studios",
        "AI research labs",
        "Large language model training",
        "Extreme simulation (CFD, FEA)",
        "Those who simply want THE BEST",
        "Sith Lords with generous budgets"
    ],
    use_cases=[
        "Training custom LLMs (13B-70B+ parameters)",
        "Running multiple 70B models simultaneously",
        "8K RAW video editing in real-time",
        "Full Pixar-quality 3D rendering",
        "Molecular dynamics simulations",
        "Climate modeling",
        "Building your own Skynet"
    ],
    performance_notes=[
        "Dual RTX 4090: 48GB combined VRAM for AI",
        "256GB RAM: Run entire datasets in memory",
        "Threadripper PRO: 64 cores for maximum parallelism",
        "15+ TB NVMe: Never run out of fast storage",
        "Custom loop: Whisper quiet under full load"
    ],
    components=[
        Component(
            category="CPU",
            name="AMD Ryzen Threadripper PRO 7995WX",
            model="sWRX90",
            price=9999.00,
            specs={
                "cores": 96,
                "threads": 192,
                "base_clock": "2.5 GHz",
                "boost_clock": "5.1 GHz",
                "l3_cache": "384MB",
                "tdp": "350W",
                "pcie_lanes": 128,
                "memory_channels": 8,
                "architecture": "Zen 4"
            },
            notes="96 CORES. UNLIMITED POWER!"
        ),
        Component(
            category="GPU Primary",
            name="NVIDIA GeForce RTX 4090",
            model="ASUS ROG STRIX LC OC (Liquid Cooled)",
            price=2499.00,
            specs={
                "vram": "24GB GDDR6X",
                "cuda_cores": 16384,
                "tensor_cores": 512,
                "boost_clock": "2640 MHz",
                "cooling": "AIO Liquid",
                "tdp": "450W"
            },
            notes="Liquid cooled for maximum sustained performance"
        ),
        Component(
            category="GPU Secondary",
            name="NVIDIA GeForce RTX 4090",
            model="ASUS ROG STRIX LC OC (Liquid Cooled)",
            price=2499.00,
            specs={
                "vram": "24GB GDDR6X",
                "cuda_cores": 16384,
                "tensor_cores": 512,
                "purpose": "48GB total VRAM for LLMs"
            },
            notes="Second liquid-cooled 4090 for AI/ML workloads"
        ),
        Component(
            category="RAM",
            name="Kingston Server Premier",
            model="512GB (8x64GB) DDR5-4800 ECC RDIMM",
            price=2999.00,
            specs={
                "capacity": "512GB",
                "speed": "4800MHz",
                "type": "DDR5 ECC Registered",
                "channels": "8-channel",
                "ecc": True
            },
            notes="Half a terabyte of ECC memory - load entire LLMs in RAM"
        ),
        Component(
            category="Storage Primary",
            name="Solidigm P44 Pro",
            model="4TB NVMe x4 (RAID 0)",
            price=1396.00,
            specs={
                "capacity": "16TB total",
                "configuration": "4x 4TB RAID 0",
                "read_speed": "28000+ MB/s (combined)",
                "interface": "NVMe PCIe 4.0"
            },
            notes="Insane read speeds for dataset loading"
        ),
        Component(
            category="Storage Secondary",
            name="Crucial T700",
            model="4TB PCIe 5.0 x2",
            price=998.00,
            specs={
                "capacity": "8TB total",
                "interface": "NVMe PCIe 5.0",
                "read_speed": "12400 MB/s each"
            },
            notes="Fastest SSDs for scratch and active projects"
        ),
        Component(
            category="Storage Tertiary",
            name="Seagate Exos X24",
            model="24TB Enterprise HDD x4",
            price=1596.00,
            specs={
                "capacity": "96TB total",
                "configuration": "4x 24TB",
                "raid_option": "RAID 5/6",
                "rpm": 7200
            },
            notes="Nearly 100TB of enterprise archive storage"
        ),
        Component(
            category="Motherboard",
            name="ASUS Pro WS WRX90E-SAGE SE",
            model="WRX90 Workstation",
            price=1499.00,
            specs={
                "socket": "sWRX90",
                "chipset": "WRX90",
                "ram_slots": 8,
                "max_ram": "2TB DDR5",
                "pcie_slots": "7x PCIe 5.0",
                "m2_slots": 4,
                "10gbe": "Dual",
                "power_stages": "16+3"
            },
            notes="Workstation-class board for Threadripper PRO"
        ),
        Component(
            category="PSU",
            name="be quiet! Dark Power Pro 13",
            model="1600W 80+ Titanium",
            price=499.00,
            specs={
                "wattage": "1600W",
                "efficiency": "80+ Titanium",
                "modular": True,
                "noise_level": "Silent",
                "warranty": "10 years"
            },
            notes="Whisper quiet even at full load"
        ),
        Component(
            category="PSU Secondary",
            name="be quiet! Dark Power Pro 13",
            model="1600W 80+ Titanium",
            price=499.00,
            specs={
                "wattage": "1600W",
                "purpose": "Dedicated GPU power",
                "combined_wattage": "3200W total"
            },
            notes="Dual PSU for extreme power demands"
        ),
        Component(
            category="Case",
            name="Caselabs Magnum THW10",
            model="Ultra Tower (Custom Order)",
            price=1299.00,
            specs={
                "form_factor": "SSI-EEB / E-ATX",
                "material": "Aluminum",
                "radiator_support": "4x 480mm",
                "drive_bays": "20+",
                "weight": "50+ lbs empty"
            },
            notes="Legendary case for legendary builds (or equivalent custom)"
        ),
        Component(
            category="Cooling",
            name="Custom Loop - Full EKWB Quantum",
            model="CPU + Dual GPU + VRM + M.2",
            price=3499.00,
            specs={
                "type": "Custom Hard Tube - Dual Loop",
                "cpu_loop": {
                    "radiator": "480mm + 360mm",
                    "block": "EK-Quantum Magnitude",
                    "pump": "D5 Dual"
                },
                "gpu_loop": {
                    "radiator": "2x 480mm",
                    "blocks": "2x EK-Quantum Vector²",
                    "pump": "D5 Dual"
                },
                "fittings": "Nickel + Acrylic",
                "tubing": "PETG Hard Tube",
                "coolant": "EK-CryoFuel Mystic Fog"
            },
            notes="Dual-loop custom cooling for absolute thermal perfection"
        ),
        Component(
            category="Accessories",
            name="Premium Extras Package",
            model="Various",
            price=999.00,
            specs={
                "fan_controller": "Aquacomputer OCTO",
                "flow_meter": "High-flow sensor",
                "temp_sensors": "8x inline sensors",
                "rgb_controller": "Lian Li L-Connect 3",
                "cable_extensions": "CableMod Pro ModFlex",
                "cable_color": "Imperial Red/Black",
                "additional_fans": "12x Noctua NF-A12x25"
            },
            notes="All the premium accessories"
        )
    ]
)


# =============================================================================
# COMPLETE CATALOG
# =============================================================================

PC_BUILDS_CATALOG = [
    TIER_1_SCRAPPER,
    TIER_2_BUDGET_WARRIOR,
    TIER_3_SOLID_PERFORMER,
    TIER_4_POWER_PLAYER,
    TIER_5_BEAST,
    TIER_6_TITAN,
    TIER_7_UNLIMITED_POWER
]


def get_build_by_tier(tier: BuildTier) -> PCBuild:
    """Get a build by its tier"""
    for build in PC_BUILDS_CATALOG:
        if build.tier == tier:
            return build
    return None


def get_builds_in_budget(budget: float) -> List[PCBuild]:
    """Get all builds that fit within a budget"""
    return [b for b in PC_BUILDS_CATALOG if b.total_price <= budget]


def print_build_summary(build: PCBuild):
    """Print a formatted build summary"""
    print("=" * 70)
    print(f"TIER {list(BuildTier).index(build.tier) + 1}: {build.name.upper()}")
    print(f'"{build.tagline}"')
    print("=" * 70)
    print(f"\nPrice Range: {build.price_range}")
    print(f"Estimated Total: ${build.total_price:,.2f}")
    print(f"\n{build.description.strip()}")

    print("\n--- TARGET AUDIENCE ---")
    for audience in build.target_audience:
        print(f"  - {audience}")

    print("\n--- USE CASES ---")
    for use_case in build.use_cases:
        print(f"  - {use_case}")

    print("\n--- COMPONENTS ---")
    for component in build.components:
        print(f"\n  [{component.category.upper()}]")
        print(f"    {component.name}")
        print(f"    Model: {component.model}")
        print(f"    Price: ${component.price:,.2f}")
        if component.notes:
            print(f"    Notes: {component.notes}")

    print("\n--- PERFORMANCE NOTES ---")
    for note in build.performance_notes:
        print(f"  - {note}")

    print("\n")


def export_to_json(filename: str = "pc_builds_catalog.json"):
    """Export catalog to JSON"""
    data = {
        "catalog_version": "1.0.0",
        "last_updated": "2024-12-30",
        "builds": [build.to_dict() for build in PC_BUILDS_CATALOG]
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Catalog exported to {filename}")


def main():
    """Display all builds"""
    print("\n" + "=" * 70)
    print("  PC BUILDS CATALOG - FROM SCRAPPER TO UNLIMITED POWER!")
    print("  7 Tiers of Computing Excellence")
    print("=" * 70 + "\n")

    for build in PC_BUILDS_CATALOG:
        print(f"\n{'='*70}")
        print(f"TIER {list(BuildTier).index(build.tier) + 1}: {build.name}")
        print(f"'{build.tagline}'")
        print(f"Price Range: {build.price_range}")
        print(f"Estimated Total: ${build.total_price:,.2f}")
        print("-" * 70)

        # Key components summary
        cpu = next((c for c in build.components if c.category == "CPU"), None)
        gpu = next((c for c in build.components if "GPU" in c.category), None)
        ram = next((c for c in build.components if c.category == "RAM"), None)
        storage = next((c for c in build.components if "Storage" in c.category), None)

        if cpu:
            print(f"CPU: {cpu.name}")
        if gpu:
            print(f"GPU: {gpu.name}")
        if ram:
            print(f"RAM: {ram.specs.get('capacity', 'N/A')}")
        if storage:
            print(f"Storage: {storage.model}")

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    for build in PC_BUILDS_CATALOG:
        tier_num = list(BuildTier).index(build.tier) + 1
        print(f"  Tier {tier_num}: {build.name:25} ${build.total_price:>10,.2f}")

    print("=" * 70)
    total_if_bought_all = sum(b.total_price for b in PC_BUILDS_CATALOG)
    print(f"  {'TOTAL (if you bought all):':30} ${total_if_bought_all:>10,.2f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
