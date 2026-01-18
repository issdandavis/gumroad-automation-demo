"""
PC Build Compatibility Checker
==============================

Validates PC component compatibility for builds in pc_builds_catalog.py.
Checks socket compatibility, RAM support, power requirements, and more.

Integrates with Shopify connector to prevent listing incompatible bundles.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class CompatibilityStatus(Enum):
    """Compatibility check result status"""
    COMPATIBLE = "compatible"
    WARNING = "warning"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass
class CompatibilityIssue:
    """Single compatibility issue"""
    component1: str
    component2: str
    issue_type: str
    severity: CompatibilityStatus
    message: str
    suggestion: str = ""


@dataclass
class CompatibilityReport:
    """Full compatibility report for a build"""
    build_name: str
    overall_status: CompatibilityStatus
    issues: List[CompatibilityIssue]
    warnings: List[str]
    power_analysis: Dict[str, Any]
    recommendations: List[str]
    compatible: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "build_name": self.build_name,
            "overall_status": self.overall_status.value,
            "compatible": self.compatible,
            "issues": [
                {
                    "components": f"{i.component1} <-> {i.component2}",
                    "type": i.issue_type,
                    "severity": i.severity.value,
                    "message": i.message,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ],
            "warnings": self.warnings,
            "power_analysis": self.power_analysis,
            "recommendations": self.recommendations
        }


# =============================================================================
# COMPATIBILITY DATABASES
# =============================================================================

# CPU Socket to Chipset mappings
SOCKET_CHIPSET_MAP = {
    # Intel
    "LGA 1150": ["H81", "B85", "H87", "Z87", "H97", "Z97"],
    "LGA 1151": ["H110", "B150", "H170", "Z170", "B250", "H270", "Z270",
                 "H310", "B360", "H370", "Z370", "B365", "Z390"],
    "LGA 1151v2": ["H310", "B360", "H370", "Z370", "B365", "Z390"],
    "LGA 1200": ["H410", "B460", "H470", "Z490", "H510", "B560", "H570", "Z590"],
    "LGA 1700": ["H610", "B660", "H670", "Z690", "B760", "Z790"],
    "LGA 2066": ["X299"],
    # AMD
    "AM4": ["A320", "B350", "X370", "B450", "X470", "A520", "B550", "X570"],
    "AM5": ["A620", "B650", "B650E", "X670", "X670E"],
    "sTRX4": ["TRX40"],
    "sWRX8": ["WRX80", "WRX90"],
    "SP5": ["WRX90"],
}

# CPU generations and their sockets
CPU_SOCKET_MAP = {
    # Intel Core (Desktop)
    r"i[3579]-4\d{3}": "LGA 1150",      # 4th gen Haswell
    r"i[3579]-5\d{3}": "LGA 1150",      # 5th gen Broadwell
    r"i[3579]-6\d{3}": "LGA 1151",      # 6th gen Skylake
    r"i[3579]-7\d{3}": "LGA 1151",      # 7th gen Kaby Lake
    r"i[3579]-8\d{3}": "LGA 1151v2",    # 8th gen Coffee Lake
    r"i[3579]-9\d{3}": "LGA 1151v2",    # 9th gen Coffee Lake Refresh
    r"i[3579]-10\d{3}": "LGA 1200",     # 10th gen Comet Lake
    r"i[3579]-11\d{3}": "LGA 1200",     # 11th gen Rocket Lake
    r"i[3579]-12\d{3}": "LGA 1700",     # 12th gen Alder Lake
    r"i[3579]-13\d{3}": "LGA 1700",     # 13th gen Raptor Lake
    r"i[3579]-14\d{3}": "LGA 1700",     # 14th gen Raptor Lake Refresh
    # AMD Ryzen
    r"Ryzen [3579] [12]\d{3}": "AM4",   # Ryzen 1000/2000 series
    r"Ryzen [3579] [34]\d{3}": "AM4",   # Ryzen 3000/4000 series
    r"Ryzen [3579] 5\d{3}": "AM4",      # Ryzen 5000 series
    r"Ryzen [3579] 7\d{3}": "AM5",      # Ryzen 7000 series
    r"Ryzen [3579] 8\d{3}": "AM5",      # Ryzen 8000 series
    r"Ryzen [3579] 9\d{3}X3D": "AM5",   # Ryzen 9000 X3D
    r"Ryzen [3579] 9\d{3}": "AM5",      # Ryzen 9000 series
    r"Threadripper": "sTRX4",            # Threadripper
    r"Threadripper PRO 7": "sWRX8",      # Threadripper PRO 7000
    r"Threadripper PRO 5": "sWRX8",      # Threadripper PRO 5000
}

# RAM type by generation
RAM_TYPE_SUPPORT = {
    "LGA 1150": ["DDR3"],
    "LGA 1151": ["DDR4", "DDR3L"],
    "LGA 1151v2": ["DDR4"],
    "LGA 1200": ["DDR4"],
    "LGA 1700": ["DDR4", "DDR5"],
    "LGA 2066": ["DDR4"],
    "AM4": ["DDR4"],
    "AM5": ["DDR5"],
    "sTRX4": ["DDR4"],
    "sWRX8": ["DDR5", "DDR4"],
}

# GPU power requirements (approximate TDP in watts)
GPU_POWER_MAP = {
    r"GTX 750": 60,
    r"GTX 1050": 75,
    r"GTX 1060": 120,
    r"GTX 1070": 150,
    r"GTX 1080": 180,
    r"RTX 2060": 160,
    r"RTX 2070": 185,
    r"RTX 2080": 225,
    r"RTX 3060": 170,
    r"RTX 3070": 220,
    r"RTX 3080": 320,
    r"RTX 3090": 350,
    r"RTX 4060": 115,
    r"RTX 4070": 200,
    r"RTX 4080": 320,
    r"RTX 4090": 450,
    r"RX 5\d{3}": 180,
    r"RX 6[678]\d{2}": 200,
    r"RX 6900": 300,
    r"RX 7\d{3}": 250,
    r"RX 7900": 355,
}

# CPU power requirements (TDP in watts)
CPU_POWER_MAP = {
    r"i[35]-": 65,
    r"i7-": 95,
    r"i9-": 125,
    r"Ryzen [35] ": 65,
    r"Ryzen 7 ": 105,
    r"Ryzen 9 ": 170,
    r"Threadripper": 280,
    r"Threadripper PRO 7995": 350,
}


class PCCompatibilityChecker:
    """
    Validates compatibility between PC components.
    Checks socket, RAM, power, and form factor compatibility.
    """

    def __init__(self):
        self.socket_chipset_map = SOCKET_CHIPSET_MAP
        self.cpu_socket_map = CPU_SOCKET_MAP
        self.ram_type_support = RAM_TYPE_SUPPORT

    def check_build_compatibility(self, build: Dict[str, Any]) -> CompatibilityReport:
        """
        Check full compatibility of a PC build.

        Args:
            build: Dictionary with 'name' and 'components' list

        Returns:
            CompatibilityReport with all findings
        """
        issues = []
        warnings = []
        recommendations = []

        build_name = build.get("name", "Unknown Build")
        components = build.get("components", [])

        # Extract component data
        cpu_data = self._find_component(components, "CPU")
        gpu_data = self._find_component(components, "GPU")
        ram_data = self._find_component(components, "RAM")
        mobo_data = self._find_component(components, "Motherboard")
        psu_data = self._find_component(components, "PSU")
        case_data = self._find_component(components, "Case")
        storage_data = self._find_component(components, "Storage")

        # Check CPU-Motherboard socket compatibility
        if cpu_data and mobo_data:
            socket_issues = self._check_socket_compatibility(cpu_data, mobo_data)
            issues.extend(socket_issues)

        # Check RAM compatibility
        if ram_data and mobo_data:
            ram_issues = self._check_ram_compatibility(ram_data, mobo_data, cpu_data)
            issues.extend(ram_issues)

        # Check power supply adequacy
        power_analysis = self._analyze_power_requirements(
            cpu_data, gpu_data, components, psu_data
        )
        if power_analysis.get("insufficient"):
            issues.append(CompatibilityIssue(
                component1="PSU",
                component2="System",
                issue_type="power",
                severity=CompatibilityStatus.INCOMPATIBLE,
                message=power_analysis["message"],
                suggestion=power_analysis["suggestion"]
            ))
        elif power_analysis.get("warning"):
            warnings.append(power_analysis["warning"])

        # Check case form factor
        if case_data and mobo_data:
            case_issues = self._check_case_compatibility(case_data, mobo_data, gpu_data)
            issues.extend(case_issues)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            issues, warnings, power_analysis, components
        )

        # Determine overall status
        if any(i.severity == CompatibilityStatus.INCOMPATIBLE for i in issues):
            overall_status = CompatibilityStatus.INCOMPATIBLE
        elif any(i.severity == CompatibilityStatus.WARNING for i in issues) or warnings:
            overall_status = CompatibilityStatus.WARNING
        elif not issues:
            overall_status = CompatibilityStatus.COMPATIBLE
        else:
            overall_status = CompatibilityStatus.UNKNOWN

        return CompatibilityReport(
            build_name=build_name,
            overall_status=overall_status,
            issues=issues,
            warnings=warnings,
            power_analysis=power_analysis,
            recommendations=recommendations,
            compatible=overall_status != CompatibilityStatus.INCOMPATIBLE
        )

    def _find_component(
        self,
        components: List[Dict],
        category: str
    ) -> Optional[Dict]:
        """Find component by category"""
        for comp in components:
            if comp.get("category", "").lower() == category.lower():
                return comp
        return None

    def _check_socket_compatibility(
        self,
        cpu: Dict,
        motherboard: Dict
    ) -> List[CompatibilityIssue]:
        """Check CPU-Motherboard socket compatibility"""
        issues = []

        cpu_name = cpu.get("name", "") + " " + cpu.get("model", "")
        mobo_specs = motherboard.get("specs", {})

        # Try to determine CPU socket
        cpu_socket = cpu.get("specs", {}).get("socket", "")
        if not cpu_socket:
            cpu_socket = self._detect_cpu_socket(cpu_name)

        # Get motherboard socket
        mobo_socket = mobo_specs.get("socket", "")

        if cpu_socket and mobo_socket:
            if cpu_socket != mobo_socket:
                issues.append(CompatibilityIssue(
                    component1=f"CPU ({cpu_socket})",
                    component2=f"Motherboard ({mobo_socket})",
                    issue_type="socket",
                    severity=CompatibilityStatus.INCOMPATIBLE,
                    message=f"CPU socket {cpu_socket} is incompatible with motherboard socket {mobo_socket}",
                    suggestion=f"Choose a motherboard with {cpu_socket} socket or a different CPU"
                ))
        elif not cpu_socket or not mobo_socket:
            issues.append(CompatibilityIssue(
                component1="CPU",
                component2="Motherboard",
                issue_type="socket",
                severity=CompatibilityStatus.UNKNOWN,
                message="Could not determine socket compatibility - verify manually",
                suggestion="Check manufacturer specifications for socket type"
            ))

        # Check chipset compatibility
        mobo_chipset = mobo_specs.get("chipset", "")
        if cpu_socket and mobo_chipset:
            compatible_chipsets = self.socket_chipset_map.get(cpu_socket, [])
            # Check if any compatible chipset matches
            chipset_match = any(
                cs.lower() in mobo_chipset.lower()
                for cs in compatible_chipsets
            )
            if compatible_chipsets and not chipset_match:
                issues.append(CompatibilityIssue(
                    component1=f"CPU ({cpu_socket})",
                    component2=f"Motherboard ({mobo_chipset})",
                    issue_type="chipset",
                    severity=CompatibilityStatus.WARNING,
                    message=f"Chipset {mobo_chipset} may not be optimal for {cpu_socket}",
                    suggestion=f"Recommended chipsets: {', '.join(compatible_chipsets[:3])}"
                ))

        return issues

    def _detect_cpu_socket(self, cpu_name: str) -> str:
        """Detect CPU socket from name"""
        for pattern, socket in self.cpu_socket_map.items():
            if re.search(pattern, cpu_name, re.IGNORECASE):
                return socket
        return ""

    def _check_ram_compatibility(
        self,
        ram: Dict,
        motherboard: Dict,
        cpu: Optional[Dict]
    ) -> List[CompatibilityIssue]:
        """Check RAM compatibility with motherboard and CPU"""
        issues = []

        ram_specs = ram.get("specs", {})
        mobo_specs = motherboard.get("specs", {})

        # Get RAM type
        ram_type = ram_specs.get("type", "")
        if not ram_type:
            ram_name = ram.get("name", "") + " " + ram.get("model", "")
            if "DDR5" in ram_name:
                ram_type = "DDR5"
            elif "DDR4" in ram_name:
                ram_type = "DDR4"
            elif "DDR3" in ram_name:
                ram_type = "DDR3"

        # Get motherboard socket for RAM type check
        mobo_socket = mobo_specs.get("socket", "")

        if ram_type and mobo_socket:
            supported_ram = self.ram_type_support.get(mobo_socket, [])
            if supported_ram and ram_type not in supported_ram:
                issues.append(CompatibilityIssue(
                    component1=f"RAM ({ram_type})",
                    component2=f"Motherboard ({mobo_socket})",
                    issue_type="ram_type",
                    severity=CompatibilityStatus.INCOMPATIBLE,
                    message=f"{ram_type} is not supported by {mobo_socket} platform",
                    suggestion=f"Use {supported_ram[0]} memory instead"
                ))

        # Check RAM capacity
        ram_capacity = ram_specs.get("capacity", "")
        max_ram = mobo_specs.get("max_ram", "")

        if ram_capacity and max_ram:
            # Extract numeric values
            try:
                ram_gb = int(re.search(r"(\d+)", str(ram_capacity)).group(1))
                max_gb = int(re.search(r"(\d+)", str(max_ram)).group(1))

                if ram_gb > max_gb:
                    issues.append(CompatibilityIssue(
                        component1=f"RAM ({ram_capacity})",
                        component2=f"Motherboard (max {max_ram})",
                        issue_type="ram_capacity",
                        severity=CompatibilityStatus.INCOMPATIBLE,
                        message=f"RAM exceeds motherboard maximum of {max_ram}",
                        suggestion=f"Reduce RAM to {max_gb}GB or less"
                    ))
            except (AttributeError, ValueError):
                # Silently skip if capacity strings can't be parsed - compatibility check will be skipped
                pass

        # Check RAM slots
        ram_sticks = ram_specs.get("channels", "")
        max_slots = mobo_specs.get("ram_slots", 0)

        if ram_sticks and max_slots:
            try:
                # Try to determine number of sticks from description
                sticks = 1
                if "2x" in str(ram_sticks).lower() or "dual" in str(ram_sticks).lower():
                    sticks = 2
                elif "4x" in str(ram_sticks).lower() or "quad" in str(ram_sticks).lower():
                    sticks = 4
                elif "8x" in str(ram_sticks).lower():
                    sticks = 8

                if sticks > max_slots:
                    issues.append(CompatibilityIssue(
                        component1=f"RAM ({sticks} sticks)",
                        component2=f"Motherboard ({max_slots} slots)",
                        issue_type="ram_slots",
                        severity=CompatibilityStatus.INCOMPATIBLE,
                        message=f"RAM kit has more sticks than available slots",
                        suggestion=f"Choose a kit with {max_slots} or fewer modules"
                    ))
            except (AttributeError, ValueError):
                # Silently skip if RAM stick count can't be determined from description
                pass

        return issues

    def _analyze_power_requirements(
        self,
        cpu: Optional[Dict],
        gpu: Optional[Dict],
        components: List[Dict],
        psu: Optional[Dict]
    ) -> Dict[str, Any]:
        """Analyze power requirements for the build"""

        # Estimate component power draw
        cpu_power = 65  # Default
        gpu_power = 75  # Default
        other_power = 100  # RAM, storage, fans, etc.

        if cpu:
            cpu_name = cpu.get("name", "") + " " + cpu.get("model", "")
            cpu_tdp = cpu.get("specs", {}).get("tdp", "")

            if cpu_tdp:
                try:
                    cpu_power = int(re.search(r"(\d+)", str(cpu_tdp)).group(1))
                except (AttributeError, ValueError):
                    # Fall through to pattern matching if TDP string can't be parsed
                    pass
            else:
                # Estimate from patterns
                for pattern, power in CPU_POWER_MAP.items():
                    if re.search(pattern, cpu_name, re.IGNORECASE):
                        cpu_power = power
                        break

        if gpu:
            gpu_name = gpu.get("name", "") + " " + gpu.get("model", "")
            gpu_tdp = gpu.get("specs", {}).get("tdp", "")

            if gpu_tdp:
                try:
                    gpu_power = int(re.search(r"(\d+)", str(gpu_tdp)).group(1))
                except (AttributeError, ValueError):
                    # Fall through to pattern matching if TDP string can't be parsed
                    pass
            else:
                for pattern, power in GPU_POWER_MAP.items():
                    if re.search(pattern, gpu_name, re.IGNORECASE):
                        gpu_power = power
                        break

        # Calculate total with 20% headroom
        estimated_draw = cpu_power + gpu_power + other_power
        recommended_psu = int(estimated_draw * 1.2)

        # Check PSU capacity
        psu_wattage = 500  # Default
        if psu:
            psu_specs = psu.get("specs", {})
            psu_wattage_str = psu_specs.get("wattage", "")
            psu_name = psu.get("name", "") + " " + psu.get("model", "")

            try:
                if psu_wattage_str:
                    psu_wattage = int(re.search(r"(\d+)", str(psu_wattage_str)).group(1))
                else:
                    match = re.search(r"(\d+)\s*W", psu_name, re.IGNORECASE)
                    if match:
                        psu_wattage = int(match.group(1))
            except (AttributeError, ValueError):
                # Keep default 0 value if wattage can't be extracted from specs or name
                pass

        # Analysis result
        result = {
            "cpu_power": cpu_power,
            "gpu_power": gpu_power,
            "other_power": other_power,
            "total_estimated": estimated_draw,
            "recommended_psu": recommended_psu,
            "actual_psu": psu_wattage,
            "headroom_percent": round((psu_wattage - estimated_draw) / psu_wattage * 100, 1)
        }

        if psu_wattage < estimated_draw:
            result["insufficient"] = True
            result["message"] = f"PSU ({psu_wattage}W) insufficient for estimated {estimated_draw}W draw"
            result["suggestion"] = f"Upgrade to at least {recommended_psu}W PSU"
        elif psu_wattage < recommended_psu:
            result["warning"] = f"PSU ({psu_wattage}W) has minimal headroom. Recommended: {recommended_psu}W"
        else:
            result["adequate"] = True

        return result

    def _check_case_compatibility(
        self,
        case: Dict,
        motherboard: Dict,
        gpu: Optional[Dict]
    ) -> List[CompatibilityIssue]:
        """Check case compatibility with motherboard and GPU"""
        issues = []

        case_specs = case.get("specs", {})
        mobo_specs = motherboard.get("specs", {})

        # Form factor compatibility
        case_form = case_specs.get("form_factor", "").lower()
        mobo_form = mobo_specs.get("form_factor", "").lower()

        # Form factor hierarchy (larger can fit smaller)
        form_factor_sizes = {
            "full tower": 5,
            "mid tower": 4,
            "atx mid-tower": 4,
            "mini tower": 3,
            "micro atx": 2,
            "mini itx": 1,
            "sff": 1
        }

        mobo_sizes = {
            "e-atx": 5,
            "eatx": 5,
            "atx": 4,
            "micro-atx": 3,
            "micro atx": 3,
            "matx": 3,
            "mini-itx": 2,
            "mini itx": 2,
            "itx": 2
        }

        case_size = 0
        mobo_size = 0

        for form, size in form_factor_sizes.items():
            if form in case_form:
                case_size = size
                break

        for form, size in mobo_sizes.items():
            if form in mobo_form:
                mobo_size = size
                break

        if case_size > 0 and mobo_size > 0:
            if mobo_size > case_size:
                issues.append(CompatibilityIssue(
                    component1=f"Case ({case_form})",
                    component2=f"Motherboard ({mobo_form})",
                    issue_type="form_factor",
                    severity=CompatibilityStatus.INCOMPATIBLE,
                    message=f"Motherboard too large for case",
                    suggestion="Choose a larger case or smaller motherboard"
                ))

        # GPU clearance (if we have data)
        if gpu:
            gpu_specs = gpu.get("specs", {})
            gpu_length = gpu_specs.get("length_mm", 0)
            case_clearance = case_specs.get("gpu_clearance_mm", 0)

            if gpu_length and case_clearance:
                if gpu_length > case_clearance:
                    issues.append(CompatibilityIssue(
                        component1=f"GPU ({gpu_length}mm)",
                        component2=f"Case ({case_clearance}mm clearance)",
                        issue_type="gpu_clearance",
                        severity=CompatibilityStatus.INCOMPATIBLE,
                        message=f"GPU too long for case",
                        suggestion="Choose a shorter GPU or larger case"
                    ))

        return issues

    def _generate_recommendations(
        self,
        issues: List[CompatibilityIssue],
        warnings: List[str],
        power_analysis: Dict,
        components: List[Dict]
    ) -> List[str]:
        """Generate build recommendations"""
        recommendations = []

        # Based on issues
        if any(i.issue_type == "socket" for i in issues):
            recommendations.append("Verify CPU and motherboard socket compatibility before purchasing")

        if any(i.issue_type == "ram_type" for i in issues):
            recommendations.append("Double-check RAM type (DDR4 vs DDR5) for your platform")

        if any(i.issue_type == "power" for i in issues):
            psu_rec = power_analysis.get("recommended_psu", 650)
            recommendations.append(f"Upgrade PSU to at least {psu_rec}W for stable operation")

        # General recommendations
        headroom = power_analysis.get("headroom_percent", 0)
        if headroom < 20:
            recommendations.append("Consider higher wattage PSU for future upgrades")

        if not any(c.get("category") == "CPU Cooler" for c in components):
            # Check if using stock cooler
            cpu = self._find_component(components, "CPU")
            if cpu:
                cpu_name = cpu.get("name", "").lower()
                if any(x in cpu_name for x in ["i9", "i7", "ryzen 9", "ryzen 7", "threadripper"]):
                    recommendations.append("Consider aftermarket CPU cooler for optimal thermal performance")

        # SSD recommendation
        storage = self._find_component(components, "Storage")
        if storage:
            storage_name = (storage.get("name", "") + storage.get("model", "")).lower()
            if "hdd" in storage_name and "ssd" not in storage_name:
                recommendations.append("Add an SSD for significantly faster boot and load times")

        if not recommendations:
            recommendations.append("Build looks good! All components appear compatible")

        return recommendations


def check_build(build_dict: Dict[str, Any]) -> CompatibilityReport:
    """
    Quick function to check a build's compatibility.

    Args:
        build_dict: Build dictionary with 'name' and 'components'

    Returns:
        CompatibilityReport
    """
    checker = PCCompatibilityChecker()
    return checker.check_build_compatibility(build_dict)


def demo():
    """Demonstrate compatibility checker"""
    print("=" * 70)
    print("PC BUILD COMPATIBILITY CHECKER DEMO")
    print("=" * 70)

    # Test build 1: Compatible modern build
    test_build_1 = {
        "name": "Modern Gaming PC",
        "components": [
            {
                "category": "CPU",
                "name": "Intel Core i7-14700K",
                "model": "Raptor Lake Refresh",
                "specs": {"socket": "LGA 1700", "tdp": "125W"}
            },
            {
                "category": "Motherboard",
                "name": "ASUS ROG Strix Z790-E",
                "model": "Z790 Chipset",
                "specs": {
                    "socket": "LGA 1700",
                    "chipset": "Z790",
                    "ram_slots": 4,
                    "max_ram": "128GB",
                    "form_factor": "ATX"
                }
            },
            {
                "category": "RAM",
                "name": "G.Skill Trident Z5 DDR5-6000",
                "model": "32GB (2x16GB)",
                "specs": {"type": "DDR5", "capacity": "32GB", "channels": "2x16GB"}
            },
            {
                "category": "GPU",
                "name": "NVIDIA RTX 4080",
                "model": "Founders Edition",
                "specs": {"tdp": "320W"}
            },
            {
                "category": "PSU",
                "name": "Corsair RM850x",
                "model": "850W 80+ Gold",
                "specs": {"wattage": "850W"}
            },
            {
                "category": "Case",
                "name": "Fractal Design Meshify 2",
                "model": "Mid Tower",
                "specs": {"form_factor": "ATX Mid-Tower", "gpu_clearance_mm": 467}
            }
        ]
    }

    # Test build 2: Incompatible (wrong RAM type)
    test_build_2 = {
        "name": "Mismatched Build",
        "components": [
            {
                "category": "CPU",
                "name": "AMD Ryzen 7 7800X3D",
                "model": "AM5",
                "specs": {"socket": "AM5", "tdp": "120W"}
            },
            {
                "category": "Motherboard",
                "name": "ASUS ROG Strix B650-A",
                "model": "B650",
                "specs": {
                    "socket": "AM5",
                    "chipset": "B650",
                    "ram_slots": 4,
                    "max_ram": "128GB",
                    "form_factor": "ATX"
                }
            },
            {
                "category": "RAM",
                "name": "Corsair Vengeance DDR4-3200",  # Wrong RAM type!
                "model": "32GB (2x16GB)",
                "specs": {"type": "DDR4", "capacity": "32GB"}
            },
            {
                "category": "GPU",
                "name": "NVIDIA RTX 4090",
                "model": "Founders Edition",
                "specs": {"tdp": "450W"}
            },
            {
                "category": "PSU",
                "name": "Cheap 500W PSU",  # Underpowered!
                "model": "Generic",
                "specs": {"wattage": "500W"}
            },
            {
                "category": "Case",
                "name": "Mini ITX Case",  # Too small!
                "model": "Compact",
                "specs": {"form_factor": "Mini ITX", "gpu_clearance_mm": 280}
            }
        ]
    }

    checker = PCCompatibilityChecker()

    for build in [test_build_1, test_build_2]:
        print(f"\n{'='*70}")
        print(f"BUILD: {build['name']}")
        print("-" * 70)

        report = checker.check_build_compatibility(build)

        status_icons = {
            CompatibilityStatus.COMPATIBLE: "✅",
            CompatibilityStatus.WARNING: "⚠️",
            CompatibilityStatus.INCOMPATIBLE: "❌",
            CompatibilityStatus.UNKNOWN: "❓"
        }

        icon = status_icons.get(report.overall_status, "❓")
        print(f"\nStatus: {icon} {report.overall_status.value.upper()}")
        print(f"Compatible: {'Yes' if report.compatible else 'No'}")

        if report.issues:
            print(f"\nIssues Found: {len(report.issues)}")
            for issue in report.issues:
                sev_icon = status_icons.get(issue.severity, "❓")
                print(f"  {sev_icon} [{issue.issue_type}] {issue.message}")
                if issue.suggestion:
                    print(f"      -> {issue.suggestion}")

        if report.warnings:
            print(f"\nWarnings:")
            for warning in report.warnings:
                print(f"  ⚠️ {warning}")

        print(f"\nPower Analysis:")
        pa = report.power_analysis
        print(f"  CPU: {pa['cpu_power']}W | GPU: {pa['gpu_power']}W | Other: {pa['other_power']}W")
        print(f"  Total Estimated: {pa['total_estimated']}W")
        print(f"  PSU Capacity: {pa['actual_psu']}W")
        print(f"  Headroom: {pa['headroom_percent']}%")

        print(f"\nRecommendations:")
        for rec in report.recommendations:
            print(f"  -> {rec}")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    demo()
