 SortLab — DAA Performance Studio

An interactive B.Tech PBL project for visualizing and benchmarking sorting algorithms on student records, sensor logs, and uploaded CSV datasets.

## Standout features
- Bright gradient interface with a responsive multi-tab dashboard.
- Eight algorithms: Bubble, Selection, Insertion, Merge, Quick, Heap, Shell and Python Timsort.
- Dataset controls: synthetic records, CSV upload, random seed and four input arrangements (random, sorted, reverse-sorted, nearly sorted).
- Smart algorithm suggestion with an explanation based on input size and arrangement.
- Benchmark arena with repeated trials, best and median runtime, operation counters and correctness verification.
- Interactive runtime and comparison charts.
- Bubble Sort step visualizer with a step slider and highlighted swap positions.
- Complexity matrix covering best/average/worst time, stability and auxiliary space.
- Export sorted data, benchmark CSV and a plain-text experiment report.

## Run locally
Python 3.10 or newer is recommended.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually http://localhost:8501).

## Suggested PBL demonstration flow
1. Open the synthetic student dataset and sort by marks.
2. Run the benchmark with random input and discuss median runtime.
3. Change the input arrangement to already sorted and compare Insertion/Bubble Sort.
4. Select reverse-sorted input to demonstrate a quadratic worst-case pattern.
5. Open the visualizer and move the slider through the Bubble Sort trace.
6. Open the DAA knowledge hub and explain stability and complexity.
7. Upload a CSV and export the experiment report.

## Technical notes
- Custom algorithms count key comparisons, explicit swaps and estimated assignments.
- Runtime excludes dataset loading, chart rendering and output display.
- The app reports both best and median timing across repeated trials.
- Bubble, Selection and Insertion Sort are skipped automatically above 5,000 values to avoid unexpectedly long runs.
- CSV benchmarking currently requires at least one numeric column.
- Python Timsort is a built-in production baseline, not a from-scratch implementation.
- Benchmark numbers are machine-dependent; use them to discuss trends, not as universal rankings.

## Project structure
- `app.py` — Streamlit application and instrumented algorithms
- `data/` — sample student and sensor datasets
- `PROJECT_REPORT_TEMPLATE.md` — report structure and methodology
