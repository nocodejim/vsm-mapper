Here are 3 hypothetical Value Stream Map examples for testing the generator. Copy the Mermaid code block content for each scenario into the `EXPECTED_MERMAID_OUTPUT` variable in your `test_vsm_generator.py` script to create different test cases.

**Scenario 1: Google Search Feature Rollout (Simplified)**

* Focuses on steps from idea validation to gradual rollout monitoring.
* Assumes significant parallel work and validation steps.

```mermaid
graph LR
    S0["Idea & Hypothesis"]
    S0 -->|2d| S1
    S1["UX Research & Mockups"]
    S1 -->|5d| S2
    S2["Eng Design Doc & Review"]
    S2 -->|4d| S3
    S3["Prototyping & User Study"]
    S3 -->|8d| S4
    S4["Core Implementation"]
    S4 -->|15d| S5
    S5["Integration & Canary Testing"]
    S5 -->|7d| S6
    S6["Staged Rollout & Monitoring"]

    %% Add wait times
    S0 -.->|Wait: 1d| S1
    S1 -.->|Wait: 3d| S2
    S2 -.->|Wait: 2d| S3
    S3 -.->|Wait: 5d| S4
    S4 -.->|Wait: 10d| S5
    S5 -.->|Wait: 4d| S6

    %% Add process metrics
    subgraph Metrics
        PT[Process Time: 41 units]
        LT[Lead Time: 66 units]
        FE[Flow Efficiency: 62%]
    end
'''

Input Data for Scenario 1:("Idea & Hypothesis", "2d", "")("UX Research & Mockups", "5d", "1d")("Eng Design Doc & Review", "4d", "3d")("Prototyping & User Study", "8d", "2d")("Core Implementation", "15d", "5d")("Integration & Canary Testing", "7d", "10d")("Staged Rollout & Monitoring", "0d", "4d")  (Note: Last step process time is 0 for calculation as monitoring is ongoing)(Calculation Check: PT=2+5+4+8+15+7+0=41. Wait=1+3+2+5+10+4=25. LT=41+25=66. FE=41/66=62%)

Scenario 2: Android Critical Bug Fix Process (Expedited)Focuses on rapid identification, fix, testing, and patch release.Shorter wait times due to urgency.
''' mermaid
graph LR
    S0["Bug Report Triaged (P0)"]
    S0 -->|4h| S1
    S1["Root Cause Analysis"]
    S1 -->|8h| S2
    S2["Fix Implementation"]
    S2 -->|6h| S3
    S3["Code Review & Merge"]
    S3 -->|2h| S4
    S4["Targeted Build & QA"]
    S4 -->|12h| S5
    S5["Patch Release Prep"]
    S5 -->|4h| S6
    S6["OTA Rollout"]

    %% Add wait times
    S0 -.->|Wait: 1h| S1
    S1 -.->|Wait: 2h| S2
    S2 -.->|Wait: 1h| S3
    S3 -.->|Wait: 1h| S4
    S4 -.->|Wait: 4h| S5
    S5 -.->|Wait: 2h| S6

    %% Add process metrics
    subgraph Metrics
        PT[Process Time: 36 units]
        LT[Lead Time: 47 units]
        FE[Flow Efficiency: 77%]
    end
'''
Input Data for Scenario 2:("Bug Report Triaged (P0)", "4h", "")("Root Cause Analysis", "8h", "1h")("Fix Implementation", "6h", "2h")("Code Review & Merge", "2h", "1h")("Targeted Build & QA", "12h", "1h")("Patch Release Prep", "4h", "4h")("OTA Rollout", "0h", "2h") (Last step PT=0)(Calculation Check: PT=4+8+6+2+12+4+0=36. Wait=1+2+1+1+4+2=11. LT=36+11=47. FE=36/47=77%)

Scenario 3: Pixel Hardware Component IterationIncludes hardware design, supplier interaction, and manufacturing steps.Longer lead times are typical.
''' mermaid
graph LR
    S0["Concept & Feasibility"]
    S0 -->|10d| S1
    S1["Schematic Design & Simulation"]
    S1 -->|15d| S2
    S2["Component Selection & Sourcing"]
    S2 -->|20d| S3
    S3["PCB Layout & Review"]
    S3 -->|10d| S4
    S4["Prototype Build (EVT)"]
    S4 -->|25d| S5
    S5["Validation & Testing"]
    S5 -->|30d| S6
    S6["Design Revision (DVT Prep)"]

    %% Add wait times
    S0 -.->|Wait: 5d| S1
    S1 -.->|Wait: 10d| S2
    S2 -.->|Wait: 15d| S3
    S3 -.->|Wait: 7d| S4
    S4 -.->|Wait: 20d| S5
    S5 -.->|Wait: 10d| S6

    %% Add process metrics
    subgraph Metrics
        PT[Process Time: 110 units]
        LT[Lead Time: 177 units]
        FE[Flow Efficiency: 62%]
    end
'''
Input Data for Scenario 3:("Concept & Feasibility", "10d", "")("Schematic Design & Simulation", "15d", "5d")("Component Selection & Sourcing", "20d", "10d")("PCB Layout & Review", "10d", "15d")("Prototype Build (EVT)", "25d", "7d")("Validation & Testing", "30d", "20d")("Design Revision (DVT Prep)", "0d", "10d") (Last step PT=0)*(Calculation Check: PT=10+15+20+10+25+30+0=110. Wait=5+10
