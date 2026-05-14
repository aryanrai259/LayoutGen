# Multi-Dimensional Evaluation Engine

The Evaluation Engine serves as the core auditing component of LayoutGen, calculating a weighted final grade for every generated SVG vector layout.

## 1. Final Grade Calculation
The final grade is a weighted sum of three primary metrics:
**Final Grade = (Compliance × 0.40) + (Design × 0.35) + (Sustainability × 0.25)**

### Grading Scale:
- **A+** (90-100)
- **A** (85-89), **A-** (80-84)
- **B+** (75-79), **B** (70-74), **B-** (65-69)
- **C+** (60-64), **C** (55-59), **C-** (50-54)
- **D** (40-49)
- **F** (<40)

---

## 2. Compliance Score (40% Weight)
Measures strict adherence to the Bengaluru BBMP 2003 municipal building bye-laws.

### Hard Thresholds:
- **Habitable Rooms** (Living, Bedroom, Dining): Min $9.5 m^2$ ($8.0 m^2$ for plots $\le 120 m^2$).
- **Kitchen:** Min $5.0 m^2$.
- **Bathroom:** Min $1.8 m^2$.
- **Minimum Widths:** Habitable $\ge 2.4m$, Kitchen $\ge 1.8m$, Bathroom $\ge 1.2m$.

### Penalty Structure:
- **Minor Violation** (<15% deviation): -1 point.
- **Moderate Violation** (15-30% deviation): -3 points.
- **Major Violation** (>30% deviation): -5 points.
- **Critical Violation** (Width < 0.8m - fire safety risk): -15 points.

---

## 3. Design Quality Score (35% Weight)
Calculated as the average of four sub-metrics: $D = \frac{Circulation + Beauty + Balance + Flow}{4}$

- **Circulation Score:** Evaluates hallway efficiency. Peak scores awarded for corridors comprising 12-13% of total area.
- **Beauty Score:** Evaluates room proportions. Proportions closest to the Golden Ratio ($1.618$) receive maximum points.
- **Balance Score:** Compares the geometric center against the weighted centroid of the layout. An offset of $<2\%$ achieves 100 points.
- **Flow Score:** Distance matrices between logical pairs. Excellent flow is defined as $<3m$ (e.g., Kitchen to Dining, Entrance to Living).

---

## 4. Sustainability Score (25% Weight)
Calculated as: $S = (WFR \times 0.50) + (Circulation \times 0.30) + (Material \times 0.20)$

- **WFR (Window-to-Floor Ratio):** 
  - Gold ($\ge 15\%$): 100 points
  - Silver ($10-15\%$): 75 points
  - Bronze ($<10\%$): 50 points
- **Material Efficiency:** Measured by the Wall-to-Carpet ratio. Lower ratios indicating efficient material use receive higher scores.

---

## 5. Vaastu Shastra Integration (Informational)
Vaastu scores provide cultural guidance and inform the feedback loop without heavily penalizing purely modern designs. 
- **Kitchen (Agni):** Southeast placement.
- **Master Bedroom:** Southwest placement.
- **Living Room:** Northeast or North placement.
- **Prayer Room (Ishan):** Northeast placement.
