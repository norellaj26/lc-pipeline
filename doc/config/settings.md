● Here's how the paths work:
                                                                                                                                  
  PROJECT_ROOT = Path(__file__).parent.parent                                                                                   
  __file__ is the path to settings.py itself → config/settings.py                                                                 
  .parent goes up one level → config/                                                                                             
  .parent again → lc_pipeline/ ← that's your project root                                                                         
                                                                                                                                  
  DATA_DIR        = PROJECT_ROOT / "data"           # lc_pipeline/data/
  INPUT_DIR       = DATA_DIR / "input"              # lc_pipeline/data/input/
  INTERMEDIATE_DIR = DATA_DIR / "intermediate"      # lc_pipeline/data/intermediate/
  OUTPUT_DIR      = DATA_DIR / "output"             # lc_pipeline/data/output/

  The / operator on a Path object is overloaded — it joins path segments, same as os.path.join() but cleaner.

  Why Path instead of plain strings?
  Path is OS-aware. It automatically uses \ on Windows and / on Linux/Mac, so the same code runs everywhere without string hacks.

  The key insight: everything is built relative to settings.py's location, not where you run the script from. That makes the
  project portable — move the whole folder anywhere and paths still resolve correctly.