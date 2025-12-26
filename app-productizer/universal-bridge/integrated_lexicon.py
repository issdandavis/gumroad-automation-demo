#!/usr/bin/env python3
"""
Integrated Universal Lexicon - Programming Languages + Six Sacred Tongues
The ultimate translation system combining real programming languages with fictional constructed languages
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class LanguageType(Enum):
    # Programming Languages
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"
    CSHARP = "csharp"
    JAVA = "java"
    
    # Sacred Tongues (Fictional)
    KORAELIN = "koraelin"      # The Binding Tongue
    AVALI = "avali"            # The Common Tongue  
    RUNETHIC = "runethic"      # The Ancient Tongue
    CASSISIVADAN = "cassisivadan"  # The Gnomish Tongue
    UMBROTH = "umbroth"        # The Shadow Tongue
    DRAUMRIC = "draumric"      # The Forge Tongue

@dataclass
class UniversalConstruct:
    """Universal construct that works across programming and fictional languages"""
    concept: str
    
    # Programming Languages
    python: str
    javascript: str
    go: str
    rust: str
    csharp: str
    java: str
    
    # Sacred Tongues
    koraelin: str
    avali: str
    runethic: str
    cassisivadan: str
    umbroth: str
    draumric: str
    
    description: str
    programming_usage: str
    magical_usage: str
    emotional_resonance: str

class IntegratedLexicon:
    """
    Integrated Lexicon - The Ultimate Universal Translation System
    
    Combines programming languages with fictional constructed languages,
    enabling translation between any two language types through universal concepts
    """
    
    def __init__(self):
        self.constructs = self._initialize_integrated_constructs()
        self.programming_patterns = self._initialize_programming_patterns()
        self.sacred_patterns = self._initialize_sacred_patterns()
        self.concept_bridges = self._initialize_concept_bridges()
        
    def _initialize_integrated_constructs(self) -> List[UniversalConstruct]:
        """Initialize constructs that bridge programming and fictional languages"""
        
        return [
            # Core Concepts - Function/Spell
            UniversalConstruct(
                concept="function_spell",
                # Programming
                python="def function_name():",
                javascript="function functionName() {",
                go="func functionName() {",
                rust="fn function_name() {",
                csharp="public void FunctionName() {",
                java="public void functionName() {",
                # Sacred Tongues
                koraelin="Thul'ael nav'sil",  # "Spiral-eternal diversity-together" (binding spell)
                avali="Flow-create with harmony",
                runethic="Ur-kra eth-bind",  # "High-power eternal-bind"
                cassisivadan="If-intent then-manifest",
                umbroth="Zhur'math vel'form",  # "Silence-witness pain-form"
                draumric="Grondrak'tharn form",  # "Forge-eternal form"
                description="A reusable block of code or magical incantation",
                programming_usage="Encapsulates logic for reuse and organization",
                magical_usage="Channels intent into repeatable magical effects",
                emotional_resonance="Creation, structure, power, manifestation"
            ),
            
            # Variable/Memory
            UniversalConstruct(
                concept="variable_memory",
                # Programming
                python="variable = value",
                javascript="let variable = value;",
                go="var variable Type = value",
                rust="let variable: Type = value;",
                csharp="Type variable = value;",
                java="Type variable = value;",
                # Sacred Tongues
                koraelin="Nav'een kor'hold",  # "Diversity-growth heart-hold" (memory in heart)
                avali="Memory-keep with ease",
                runethic="Eth-memory kra'hold",  # "Eternal-memory power-hold"
                cassisivadan="If-remember then-access",
                umbroth="Shul'memory pain'keep",  # "Remember-memory pain-keep"
                draumric="Mek'memory tharn'hold",  # "Structure-memory eternal-hold"
                description="Storage of data or magical energy",
                programming_usage="Stores values for later use in computation",
                magical_usage="Holds magical energy or spell components",
                emotional_resonance="Memory, preservation, potential, storage"
            ),
            
            # Loop/Ritual
            UniversalConstruct(
                concept="loop_ritual",
                # Programming
                python="for item in items:",
                javascript="for (let item of items) {",
                go="for _, item := range items {",
                rust="for item in items {",
                csharp="foreach (var item in items) {",
                java="for (Item item : items) {",
                # Sacred Tongues
                koraelin="Thul'sil nav'repeat",  # "Spiral-together diversity-repeat"
                avali="Flow-cycle with rhythm",
                runethic="Rum'cycle kra'repeat",  # "Rumble-cycle power-repeat"
                cassisivadan="Ryth'cycle if-continue",
                umbroth="Thor'cycle pain'repeat",  # "Past-cycle pain-repeat"
                draumric="Grond'cycle tharn'repeat",  # "Forge-cycle eternal-repeat"
                description="Repetitive execution of code or ritual",
                programming_usage="Iterates over collections or repeats operations",
                magical_usage="Amplifies magical effects through repetition",
                emotional_resonance="Rhythm, persistence, amplification, dedication"
            ),
            
            # Condition/Choice
            UniversalConstruct(
                concept="condition_choice",
                # Programming
                python="if condition:",
                javascript="if (condition) {",
                go="if condition {",
                rust="if condition {",
                csharp="if (condition) {",
                java="if (condition) {",
                # Sacred Tongues
                koraelin="Nav'choice kor'decide",  # "Diversity-choice heart-decide"
                avali="If-path then-choose",
                runethic="Krak'choice ur'decide",  # "Fracture-choice high-decide"
                cassisivadan="If-condition then-branch",
                umbroth="Math'choice zhur'decide",  # "Witness-choice silence-decide"
                draumric="Tharn'choice grond'decide",  # "Eternal-choice forge-decide"
                description="Conditional execution based on criteria",
                programming_usage="Controls program flow based on conditions",
                magical_usage="Directs magical energy based on circumstances",
                emotional_resonance="Decision, branching, wisdom, choice"
            ),
            
            # Error/Curse
            UniversalConstruct(
                concept="error_curse",
                # Programming
                python="try:\n    code\nexcept Exception:",
                javascript="try {\n    code\n} catch (error) {",
                go="if err != nil {",
                rust="match result {\n    Err(error) => {}",
                csharp="try {\n    code\n} catch (Exception) {",
                java="try {\n    code\n} catch (Exception e) {",
                # Sacred Tongues
                koraelin="'Zhur'break nav'heal",  # "Silence-break diversity-heal"
                avali="Error-catch with grace",
                runethic="Krak'error bind'contain",  # "Fracture-error bind-contain"
                cassisivadan="If-error then-fix",
                umbroth="Vel'curse thor'contain",  # "Pain-curse past-contain"
                draumric="Break'error grond'repair",  # "Break-error forge-repair"
                description="Handling of errors or magical mishaps",
                programming_usage="Graceful handling of runtime errors",
                magical_usage="Containing and redirecting magical backlash",
                emotional_resonance="Protection, recovery, wisdom, resilience"
            ),
            
            # Class/Entity
            UniversalConstruct(
                concept="class_entity",
                # Programming
                python="class ClassName:",
                javascript="class ClassName {",
                go="type ClassName struct {",
                rust="struct ClassName {",
                csharp="public class ClassName {",
                java="public class ClassName {",
                # Sacred Tongues
                koraelin="Nav'form sil'essence",  # "Diversity-form together-essence"
                avali="Entity-form with structure",
                runethic="Ur'form eth'essence",  # "High-form eternal-essence"
                cassisivadan="Vadan'form if-create",
                umbroth="Dark'form shul'essence",  # "Dark-form remember-essence"
                draumric="Mek'form tharn'essence",  # "Structure-form eternal-essence"
                description="Template for creating objects or entities",
                programming_usage="Defines structure and behavior of objects",
                magical_usage="Defines the essence and properties of magical beings",
                emotional_resonance="Creation, identity, structure, manifestation"
            ),
            
            # Array/Collection
            UniversalConstruct(
                concept="array_collection",
                # Programming
                python="items = [1, 2, 3]",
                javascript="let items = [1, 2, 3];",
                go="items := []int{1, 2, 3}",
                rust="let items = vec![1, 2, 3];",
                csharp="var items = new List<int> {1, 2, 3};",
                java="List<Integer> items = Arrays.asList(1, 2, 3);",
                # Sacred Tongues
                koraelin="Nav'gather sil'many",  # "Diversity-gather together-many"
                avali="Collection-hold with order",
                runethic="Ik'gather kra'many",  # "Bound-gather power-many"
                cassisivadan="Adan'collect ryth'many",
                umbroth="Ak'gather shul'many",  # "Bound-gather remember-many"
                draumric="Rak'gather mek'many",  # "Forged-gather structure-many"
                description="Collection of multiple items or entities",
                programming_usage="Stores multiple values in ordered structure",
                magical_usage="Gathers multiple magical elements or spirits",
                emotional_resonance="Unity, collection, organization, abundance"
            ),
            
            # Print/Manifest
            UniversalConstruct(
                concept="print_manifest",
                # Programming
                python="print(message)",
                javascript="console.log(message);",
                go="fmt.Println(message)",
                rust="println!(message);",
                csharp="Console.WriteLine(message);",
                java="System.out.println(message);",
                # Sacred Tongues
                koraelin="Sil'speak nav'manifest",  # "Together-speak diversity-manifest"
                avali="Speak-forth with clarity",
                runethic="Ur'speak kra'manifest",  # "High-speak power-manifest"
                cassisivadan="If-speak then-manifest",
                umbroth="Math'speak zhur'manifest",  # "Witness-speak silence-manifest"
                draumric="Grond'speak tharn'manifest",  # "Forge-speak eternal-manifest"
                description="Output information or manifest reality",
                programming_usage="Displays information to user or console",
                magical_usage="Speaks reality into existence",
                emotional_resonance="Communication, manifestation, expression, creation"
            ),
            
            # Return/Complete
            UniversalConstruct(
                concept="return_complete",
                # Programming
                python="return result",
                javascript="return result;",
                go="return result",
                rust="return result;",
                csharp="return result;",
                java="return result;",
                # Sacred Tongues
                koraelin="Thul'complete nav'return",  # "Spiral-complete diversity-return"
                avali="Complete-return with success",
                runethic="Eth'complete kra'return",  # "Eternal-complete power-return"
                cassisivadan="Then-complete ryth'return",
                umbroth="Math'complete thor'return",  # "Witness-complete past-return"
                draumric="Grond'complete tharn'return",  # "Forge-complete eternal-return"
                description="Return a result or complete a process",
                programming_usage="Returns value from function to caller",
                magical_usage="Completes spell and returns magical energy",
                emotional_resonance="Completion, fulfillment, success, closure"
            )
        ]
    
    def _initialize_programming_patterns(self) -> Dict[str, Dict[str, str]]:
        """Programming language specific patterns"""
        
        return {
            "syntax_patterns": {
                "python": {"block_start": ":", "indent": "    ", "comment": "#"},
                "javascript": {"block_start": "{", "block_end": "}", "statement_end": ";", "comment": "//"},
                "go": {"block_start": "{", "block_end": "}", "comment": "//"},
                "rust": {"block_start": "{", "block_end": "}", "statement_end": ";", "comment": "//"},
                "csharp": {"block_start": "{", "block_end": "}", "statement_end": ";", "comment": "//"},
                "java": {"block_start": "{", "block_end": "}", "statement_end": ";", "comment": "//"}
            },
            
            "type_systems": {
                "python": "dynamic",
                "javascript": "dynamic",
                "go": "static",
                "rust": "static",
                "csharp": "static",
                "java": "static"
            }
        }
    
    def _initialize_sacred_patterns(self) -> Dict[str, Dict[str, str]]:
        """Sacred Tongues specific patterns"""
        
        return {
            "magical_particles": {
                "koraelin": {"'kor": "heart", "'nav": "diversity", "'sil": "together", "'thul": "spiral", "'ael": "eternal"},
                "avali": {"flow": "continuous", "ease": "effortless", "harmony": "balanced"},
                "runethic": {"ur-": "high_power", "eth-": "eternal", "kra": "power", "-nul": "nullify"},
                "cassisivadan": {"if-": "conditional", "then-": "consequence", "ryth-": "rhythm", "vadan": "invention"},
                "umbroth": {"zhur-": "silence", "'shul": "remember", "'thor": "pain", "'math": "witness"},
                "draumric": {"grond-": "forge", "'mek": "structure", "'tharn": "eternal", "'rak": "forged"}
            },
            
            "emotional_resonance": {
                "koraelin": "unity, harmony, diversity, invitation",
                "avali": "diplomacy, flow, ease, cooperation",
                "runethic": "power, ancient wisdom, binding, hierarchy",
                "cassisivadan": "invention, chaos, rhythm, logic",
                "umbroth": "shadow, pain, memory, concealment",
                "draumric": "honor, crafting, structure, passion"
            }
        }
    
    def _initialize_concept_bridges(self) -> Dict[str, Dict[str, str]]:
        """Bridges between programming and magical concepts"""
        
        return {
            "programming_to_magic": {
                "function": "spell",
                "variable": "memory_crystal",
                "loop": "ritual_circle",
                "condition": "divination",
                "error": "curse_backlash",
                "class": "entity_template",
                "array": "spirit_collection",
                "print": "manifestation",
                "return": "spell_completion"
            },
            
            "magic_to_programming": {
                "spell": "function",
                "ritual": "loop",
                "binding": "variable_assignment",
                "manifestation": "output",
                "divination": "conditional",
                "curse": "exception",
                "entity": "object_instance",
                "collection": "array",
                "completion": "return_statement"
            }
        }
    
    def translate_construct(self, construct_name: str, from_lang: LanguageType, to_lang: LanguageType) -> Optional[str]:
        """Translate a construct between any two languages (programming or sacred)"""
        
        for construct in self.constructs:
            if construct.concept == construct_name:
                from_value = getattr(construct, from_lang.value)
                to_value = getattr(construct, to_lang.value)
                return to_value
        
        return None
    
    def translate_code_to_spell(self, code: str, from_lang: LanguageType, to_tongue: LanguageType) -> Dict[str, Any]:
        """Translate programming code into a magical spell"""
        
        if from_lang.value not in ["python", "javascript", "go", "rust", "csharp", "java"]:
            return {"error": "Source must be a programming language"}
        
        if to_tongue.value not in ["koraelin", "avali", "runethic", "cassisivadan", "umbroth", "draumric"]:
            return {"error": "Target must be a Sacred Tongue"}
        
        # Analyze code structure
        analysis = self._analyze_code_structure(code, from_lang)
        
        # Convert to magical concepts
        magical_elements = []
        for element in analysis["elements"]:
            concept = self.concept_bridges["programming_to_magic"].get(element["type"], element["type"])
            
            # Find matching construct
            for construct in self.constructs:
                if concept in construct.concept:
                    spell_part = getattr(construct, to_tongue.value)
                    magical_elements.append({
                        "original": element["code"],
                        "concept": concept,
                        "spell": spell_part,
                        "power_level": element.get("complexity", 1)
                    })
                    break
        
        # Combine into complete spell
        spell_components = [elem["spell"] for elem in magical_elements]
        complete_spell = " ".join(spell_components)
        
        # Add magical resonance
        particles = self.sacred_patterns["magical_particles"].get(to_tongue.value, {})
        resonance = self.sacred_patterns["emotional_resonance"].get(to_tongue.value, "neutral")
        
        return {
            "original_code": code,
            "source_language": from_lang.value,
            "target_tongue": to_tongue.value,
            "spell_incantation": complete_spell,
            "magical_elements": magical_elements,
            "emotional_resonance": resonance,
            "casting_instructions": f"Speak with {to_tongue.value} inflection",
            "power_level": sum(elem["power_level"] for elem in magical_elements),
            "warnings": self._get_casting_warnings(to_tongue, len(magical_elements))
        }
    
    def translate_spell_to_code(self, spell: str, from_tongue: LanguageType, to_lang: LanguageType) -> Dict[str, Any]:
        """Translate a magical spell into programming code"""
        
        if from_tongue.value not in ["koraelin", "avali", "runethic", "cassisivadan", "umbroth", "draumric"]:
            return {"error": "Source must be a Sacred Tongue"}
        
        if to_lang.value not in ["python", "javascript", "go", "rust", "csharp", "java"]:
            return {"error": "Target must be a programming language"}
        
        # Analyze spell structure
        analysis = self._analyze_spell_structure(spell, from_tongue)
        
        # Convert to programming concepts
        code_elements = []
        for element in analysis["elements"]:
            concept = self.concept_bridges["magic_to_programming"].get(element["type"], element["type"])
            
            # Find matching construct
            for construct in self.constructs:
                if concept in construct.concept:
                    code_part = getattr(construct, to_lang.value)
                    code_elements.append({
                        "original": element["spell"],
                        "concept": concept,
                        "code": code_part,
                        "complexity": element.get("power_level", 1)
                    })
                    break
        
        # Combine into complete code
        code_lines = [elem["code"] for elem in code_elements]
        complete_code = "\n".join(code_lines)
        
        # Add language-specific formatting
        syntax = self.programming_patterns["syntax_patterns"].get(to_lang.value, {})
        
        return {
            "original_spell": spell,
            "source_tongue": from_tongue.value,
            "target_language": to_lang.value,
            "generated_code": complete_code,
            "code_elements": code_elements,
            "syntax_notes": syntax,
            "complexity_level": sum(elem["complexity"] for elem in code_elements),
            "execution_notes": f"Run in {to_lang.value} environment"
        }
    
    def _analyze_code_structure(self, code: str, language: LanguageType) -> Dict[str, Any]:
        """Analyze programming code structure"""
        
        elements = []
        
        # Simple pattern matching (could be enhanced with AST parsing)
        if "def " in code or "function " in code or "func " in code:
            elements.append({"type": "function", "code": "function definition", "complexity": 2})
        
        if "for " in code or "while " in code:
            elements.append({"type": "loop", "code": "iteration", "complexity": 2})
        
        if "if " in code:
            elements.append({"type": "condition", "code": "conditional", "complexity": 1})
        
        if "print" in code or "console.log" in code or "fmt.Print" in code:
            elements.append({"type": "print", "code": "output", "complexity": 1})
        
        if "return " in code:
            elements.append({"type": "return", "code": "return statement", "complexity": 1})
        
        return {
            "language": language.value,
            "elements": elements,
            "total_complexity": sum(elem["complexity"] for elem in elements)
        }
    
    def _analyze_spell_structure(self, spell: str, tongue: LanguageType) -> Dict[str, Any]:
        """Analyze magical spell structure"""
        
        elements = []
        particles = self.sacred_patterns["magical_particles"].get(tongue.value, {})
        
        # Detect magical particles
        for particle, meaning in particles.items():
            if particle in spell:
                elements.append({
                    "type": "spell",
                    "spell": particle,
                    "meaning": meaning,
                    "power_level": 1
                })
        
        # Detect common spell patterns
        if "bind" in spell or "eth" in spell:
            elements.append({"type": "binding", "spell": "binding magic", "power_level": 3})
        
        if "manifest" in spell or "form" in spell:
            elements.append({"type": "manifestation", "spell": "creation magic", "power_level": 2})
        
        return {
            "tongue": tongue.value,
            "elements": elements,
            "total_power": sum(elem["power_level"] for elem in elements)
        }
    
    def _get_casting_warnings(self, tongue: LanguageType, complexity: int) -> List[str]:
        """Get warnings for spell casting"""
        
        warnings = []
        
        if tongue.value == "runethic":
            warnings.append("⚠️ DANGER: Runethic magic can rupture dimensions")
            if complexity > 3:
                warnings.append("⚠️ CRITICAL: High complexity may shatter reality")
        
        elif tongue.value == "umbroth":
            warnings.append("⚠️ Shadow magic may attract dark entities")
            warnings.append("⚠️ Emotional pain may be required as power source")
        
        elif tongue.value == "koraelin":
            warnings.append("⚠️ Binding magic creates permanent emotional connections")
        
        elif tongue.value == "draumric":
            warnings.append("⚠️ Forge magic creates permanent structural changes")
        
        if complexity > 5:
            warnings.append("⚠️ EXTREME: Very high complexity - recommend expert supervision")
        
        return warnings
    
    def generate_universal_translation_report(self, from_lang: LanguageType, to_lang: LanguageType) -> Dict[str, Any]:
        """Generate comprehensive translation report between any two languages"""
        
        report = {
            "from_language": from_lang.value,
            "to_language": to_lang.value,
            "language_types": {
                "from_type": "programming" if from_lang.value in ["python", "javascript", "go", "rust", "csharp", "java"] else "sacred",
                "to_type": "programming" if to_lang.value in ["python", "javascript", "go", "rust", "csharp", "java"] else "sacred"
            },
            "available_constructs": len(self.constructs),
            "construct_mappings": {},
            "special_considerations": [],
            "translation_examples": []
        }
        
        # Generate construct mappings
        for construct in self.constructs[:5]:  # First 5 for brevity
            from_value = getattr(construct, from_lang.value)
            to_value = getattr(construct, to_lang.value)
            
            report["construct_mappings"][construct.concept] = {
                "from": from_value,
                "to": to_value,
                "description": construct.description
            }
        
        # Add special considerations
        if report["language_types"]["from_type"] != report["language_types"]["to_type"]:
            report["special_considerations"].append("Cross-domain translation (programming ↔ magical)")
            
            if report["language_types"]["to_type"] == "sacred":
                report["special_considerations"].append("Code will be converted to magical concepts")
                report["special_considerations"].extend(self._get_casting_warnings(to_lang, 3))
            else:
                report["special_considerations"].append("Spell will be converted to programming logic")
        
        return report

def demo_integrated_lexicon():
    """Demonstrate the Integrated Universal Lexicon"""
    
    print("🌍✨ INTEGRATED UNIVERSAL LEXICON DEMONSTRATION")
    print("=" * 70)
    print("Programming Languages + Six Sacred Tongues = Ultimate Translation")
    print()
    
    lexicon = IntegratedLexicon()
    
    # Demo 1: Basic construct translation
    print("🔄 Demo 1: Cross-Domain Construct Translation")
    print("   Function/Spell concept across all languages:")
    
    for lang in LanguageType:
        translation = lexicon.translate_construct("function_spell", LanguageType.PYTHON, lang)
        lang_type = "📱" if lang.value in ["python", "javascript", "go", "rust", "csharp", "java"] else "✨"
        print(f"   {lang_type} {lang.value}: {translation}")
    print()
    
    # Demo 2: Code to Spell translation
    print("⚡ Demo 2: Programming Code → Magical Spell")
    python_code = """
def greet(name):
    if name:
        print(f"Hello, {name}!")
        return True
    return False
"""
    
    print(f"   Original Python code:")
    print(f"   {python_code.strip()}")
    print()
    
    # Translate to different Sacred Tongues
    for tongue in [LanguageType.KORAELIN, LanguageType.RUNETHIC, LanguageType.DRAUMRIC]:
        spell_result = lexicon.translate_code_to_spell(python_code, LanguageType.PYTHON, tongue)
        print(f"   ✨ {tongue.value.title()} Spell:")
        print(f"      {spell_result['spell_incantation']}")
        print(f"      Power Level: {spell_result['power_level']}")
        if spell_result['warnings']:
            print(f"      {spell_result['warnings'][0]}")
        print()
    
    # Demo 3: Spell to Code translation
    print("🔮 Demo 3: Magical Spell → Programming Code")
    koraelin_spell = "Thul'ael nav'sil kor'manifest"
    
    print(f"   Original Kor'aelin spell: {koraelin_spell}")
    print()
    
    # Translate to different programming languages
    for lang in [LanguageType.PYTHON, LanguageType.JAVASCRIPT, LanguageType.GO]:
        code_result = lexicon.translate_spell_to_code(koraelin_spell, LanguageType.KORAELIN, lang)
        print(f"   📱 {lang.value.title()} Code:")
        print(f"      {code_result['generated_code']}")
        print(f"      Complexity: {code_result['complexity_level']}")
        print()
    
    # Demo 4: Universal translation report
    print("📊 Demo 4: Universal Translation Report")
    report = lexicon.generate_universal_translation_report(LanguageType.PYTHON, LanguageType.RUNETHIC)
    
    print(f"   Translation: {report['from_language']} → {report['to_language']}")
    print(f"   Type: {report['language_types']['from_type']} → {report['language_types']['to_type']}")
    print(f"   Available constructs: {report['available_constructs']}")
    print(f"   Special considerations: {len(report['special_considerations'])}")
    
    print("\n   Sample construct mappings:")
    for concept, mapping in list(report['construct_mappings'].items())[:3]:
        print(f"   {concept}:")
        print(f"     From: {mapping['from']}")
        print(f"     To: {mapping['to']}")
        print()
    
    # Demo 5: Cross-language concept bridging
    print("🌉 Demo 5: Concept Bridging")
    print("   Programming → Magic:")
    for prog, magic in list(lexicon.concept_bridges["programming_to_magic"].items())[:5]:
        print(f"   {prog} → {magic}")
    
    print("\n   Magic → Programming:")
    for magic, prog in list(lexicon.concept_bridges["magic_to_programming"].items())[:5]:
        print(f"   {magic} → {prog}")
    
    print("\n🌍✨ INTEGRATED LEXICON CAPABILITIES:")
    print("   ✅ 12 total languages (6 programming + 6 sacred)")
    print("   ✅ Universal construct translation")
    print("   ✅ Code → Spell conversion")
    print("   ✅ Spell → Code conversion")
    print("   ✅ Cross-domain concept bridging")
    print("   ✅ Magical resonance analysis")
    print("   ✅ Programming pattern recognition")
    print("   ✅ Safety warnings for magical casting")
    print("   ✅ Comprehensive translation reports")
    print("   ✅ Emotional and cultural context")
    
    return lexicon

if __name__ == '__main__':
    demo_integrated_lexicon()