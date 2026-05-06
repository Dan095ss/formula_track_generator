# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->


## Project: f1_track — Parametric F1 Track Generator for Assetto Corsa

**Goal:** Generate realistic, parametrically-controlled F1 race tracks for simulation, testing, and education.

**Technology:** Python 3.12, Pydantic (validation), NumPy/SciPy (math), Matplotlib/Plotly (viz)

**Repository:** https://github.com/Dan095ss/formula_track_generator (contains ONLY f1_track files, no other projects)

---

## Project Stages (Completed)

### Stage 0.5 — RuleSet Standards ✅ COMPLETE
- FIA Appendix O constraints (F1 Grade 1, CIK-FIA Karting)
- Track length, width, corner radii, elevation, banking limits
- Segment type enumeration (10 types supported)
- **Files:** `f1_track/rules.py`

### Stage 1 — Geometry Primitives ✅ COMPLETE
- Parametric curves: Clothoid (spiral), CircularArc, Line
- G2 continuity through clothoid entry/exit spirals
- Track segments: 10 types (Straight, Hairpin, Chicane, Esses, HighSpeedTurn, Parabolica, TighteningRadius, OffCamber, BlindCrest, CircularTurn)
- **Files:** `f1_track/geometry/curve.py`, `f1_track/geometry/segment.py`

### Stage 2 — FIA Validation ✅ COMPLETE
- TrackValidator: Validates Track objects against RuleSet constraints
- ValidationError with descriptive messages per constraint
- All 6 aggregate properties checked (length, width, corner radii, elevation, banking)
- **Files:** `f1_track/geometry/validate.py`, `f1_track/geometry/track.py`

### Stage 3 — QSS Lap Time Simulator ✅ COMPLETE
- F1Car: mass (798kg), power (770kW), drag (0.95), downforce model
- MinimumCurvatureRaceline: Optimal path calculation
- LapSimulator: Quasi-steady-state simulation with grip/power speed limits
- **Files:** `f1_track/sim/car.py`, `f1_track/sim/qss.py`, `f1_track/sim/raceline.py`

### Stage 4 — Parametric Track Generator ✅ COMPLETE (THIS SESSION)
- **GenParams:** Pydantic model with 3 generation modes (DEMO, AUTO, MANUAL)
- **DemoTrack:** Reference track with all 10 segment types (~5540m, F1 Grade 1 compliant)
- **TrackComposer:** Main engine with 3 strategies:
  - DEMO: Predefined reference track
  - AUTO: Weighted-random generation by difficulty (easy/medium/hard)
  - MANUAL: User preferences (segment distribution, elevation style, target length)
- **Files:** `f1_track/generate/params.py`, `f1_track/generate/templates.py`, `f1_track/generate/composer.py`
- **Tests:** 27/27 passing in `tests/test_generate.py`
- **Documentation:** See `STAGE4_DOCUMENTATION.md`

---

## Build & Test

```bash
# Run all tests
cd C:/Users/Sevryuk.DA/Documents/CLAUDE
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_generate.py -v

# Check imports
python -c "from f1_track.generate import GenParams, Mode, TrackComposer, create_demo_track; print('✓ Stage 4 imports OK')"

# Git status and push
git status
git push
```

## Architecture Overview

```
f1_track/
├── rules.py                    # Stage 0.5: RuleSet standards
├── geometry/
│   ├── curve.py               # Stage 1: Parametric curves
│   ├── segment.py             # Stage 1: Segment types (10 types)
│   ├── track.py               # Stage 2: Track model
│   └── validate.py            # Stage 2: FIA validation
├── sim/
│   ├── car.py                 # Stage 3: F1Car model
│   ├── qss.py                 # Stage 3: QSS lap simulator
│   └── raceline.py            # Stage 3: Raceline optimizer
└── generate/
    ├── params.py              # Stage 4: GenParams model
    ├── templates.py           # Stage 4: DemoTrack factory
    └── composer.py            # Stage 4: TrackComposer engine
```

**Data Flow:**
```
GenParams (user input)
    ↓
TrackComposer.compose(params, ruleset)
    ├→ DEMO: create_demo_track()
    ├→ AUTO: _compose_auto() [weighted-random]
    └→ MANUAL: _compose_manual() [preferences]
    ↓
TrackValidator (FIA checks)
    ↓
Track object (valid or raises error)
```

## Conventions & Patterns

### Code Style
- **TDD Required:** RED → GREEN → REFACTOR → COMMIT (no exceptions)
- **No comments unless WHY is non-obvious:** Code should be self-documenting
- **Minimal dependencies:** Use stdlib, NumPy, SciPy, Pydantic only
- **Type hints throughout:** All function signatures typed

### Testing
- **Tests must pass before commit:** All stages have 100% green tests
- **Test files in `tests/`:** `test_rulesets.py`, `test_geometry.py`, `test_validate.py`, `test_sim.py`, `test_generate.py`
- **Red-Green-Refactor cycle:** Write failing test first, implement minimal code, run tests

### Git Workflow
- **Atomic commits:** Each commit implements one logical feature
- **Push after every stage:** `git push` must succeed before session ends
- **Commit messages:** Descriptive, reference stage/task ("Stage 4: ..." or "feat: ...", "fix: ...", "test: ...")
- **Co-author in commits:** Include "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"

### Documentation
- **Stage documentation:** Each stage has a `STAGE<N>_DOCUMENTATION.md` file
- **Docstrings:** Class/function docstrings with Args, Returns, Raises
- **API examples:** Every public class/function has usage example in docs

### Next Stages (TODO)

**Stage 5 — Visualization**
- 2D track plot with centerline, width, elevation profile
- 3D interactive visualization (Plotly)
- Speed profile overlay
- CLI report generation

**Post-MVP**
- Assetto Corsa `.kml` export format
- Desktop GUI (Tkinter or PyQt)
- Performance optimization for large track libraries
- Support for additional racing series (F2, IndyCar, WEC)
