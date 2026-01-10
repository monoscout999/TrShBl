# 🔧 TODO: Modular Generator Tool

## Priority: HIGH
## Status: PENDING
## Created: 2026-01-10

---

## 🎯 Objective

Create `tool/modular_generator.py` to automate the modular file generation process, eliminating manual tasks.json creation and file combination.

---

## 📋 Requirements

### Core Functionality
1. **Auto-split complex prompts** into logical modules
2. **Generate tasks.json** automatically with optimized module prompts
3. **Execute batch system** and combine results
4. **Validate** combined output

### Features
- [ ] Prompt length analyzer
- [ ] Smart split detection (by classes, functions, sections)
- [ ] Module dependency resolver
- [ ] Automatic file combination
- [ ] Post-generation validation
- [ ] Interactive mode (preview splits before executing)

---

## 💡 Proposed API

### Basic Usage
```bash
python tool/modular_generator.py --project my-app --prompt "Generate realistic fire simulator..."
```

### Advanced Usage with existing file
```bash
python tool/modular_generator.py --input prompt.txt --output-dir fire-sim --auto-split --combine
```

### Interactive Mode
```bash
python tool/modular_generator.py --interactive
# Shows proposed splits, allows editing, then executes
```

---

## 🏗️ Technical Design

### Split Detection Algorithm

**CSS:**
- Detect sections: reset, variables, layout, components, animations
- Split at `/*` comment boundaries
- Group related selectors

**JavaScript:**
- Detect: config/setup, class definitions, functions, event listeners
- Split at class/function boundaries
- Maintain dependency order

**HTML:**
- Detect: head, body sections, script includes
- Split at semantic boundaries (`<section>`, `<div id>`)

### File Structure
```python
class ModularGenerator:
    def analyze_prompt(self, prompt: str) -> PromptAnalysis
    def detect_split_points(self, analysis: PromptAnalysis) -> List[Module]
    def generate_tasks_json(self, modules: List[Module]) -> dict
    def execute_batch(self, tasks: dict) -> ExecutionReport
    def combine_modules(self, files: List[str], output: str) -> bool
    def validate_output(self, filepath: str) -> ValidationResult
```

---

## 🎯 Success Metrics

**Performance:**
- [ ] 100% success rate for modular generation
- [ ] < 30 second total time (split + generate + combine)
- [ ] Works for prompts up to 5000 characters

**Quality:**
- [ ] Combined file passes all validations
- [ ] No duplicate code in combined output
- [ ] Proper dependency order maintained

**Usability:**
- [ ] Single command execution
- [ ] Clear progress reporting
- [ ] Helpful error messages

---

## 📦 Dependencies

- `ask_agent_batch_v2.py` (existing)
- `validate_media.py` (existing)
- New: `prompt_analyzer.py` (to create)
- New: `module_combiner.py` (to create)

---

## 🚀 Implementation Phases

### Phase 1: Analyzer (Week 1)
- Create `prompt_analyzer.py`
- Implement split detection for CSS/JS
- Unit tests

### Phase 2: Generator (Week 2)
- Create main `modular_generator.py`
- Implement tasks.json generation
- Integration with batch system

### Phase 3: Combiner (Week 3)
- Create `module_combiner.py`
- Implement smart file combination
- Duplicate detection

### Phase 4: Polish (Week 4)
- Interactive mode
- Better error messages
- Documentation

---

## 📝 Example Usage

**Input prompt.txt:**
```
Generate a realistic fire simulator with flame particles, spark system, 
interactive controls (5 sliders), preset buttons, temperature gauge, 
glassmorphism UI...
[2500 characters total]
```

**Command:**
```bash
python tool/modular_generator.py --input prompt.txt --output-dir fire-sim
```

**Output:**
```
🔍 Analyzing prompt... (2500 chars detected)
📊 Optimal split: 6 modules (CSS: 3, JS: 3)
📝 Generated tasks.json with 6 tasks
⚡ Executing batch system...
   ✅ CSS-Base (0.8s)
   ✅ CSS-Controls (0.9s)
   ✅ CSS-Gauges (0.7s)
   ✅ JS-Setup (1.2s)
   ✅ JS-Classes (1.5s)
   ✅ JS-Controls (1.1s)
🔧 Combining modules...
   ✅ style.css (1547 bytes)
   ✅ script.js (4892 bytes)
✅ Validation passed
🎉 Project ready in fire-sim/
⏱️  Total time: 8.3 seconds
```

---

## 🎓 Learning from Fire Simulator V2

**What worked:**
- Manual 3-batch approach (Backend+HTML, CSS modules, JS modules)
- 100% success rate with ~200-400 char prompts
- Total time: 33.78 seconds for 12 files

**What can be automated:**
- Module splitting (currently manual)
- tasks.json creation (currently manual)
- File combination (currently manual PowerShell commands)

**Expected improvement:**
- Reduce total time from ~4 minutes to < 30 seconds
- Eliminate manual JSON editing
- One command execution

---

**Created by:** Multi-Agent System Analysis  
**Priority:** HIGH (will save significant time on future projects)  
**Estimated effort:** 2-3 weeks  
**Impact:** HIGH (game-changer for complex projects)
