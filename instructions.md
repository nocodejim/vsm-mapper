```mermaid
graph LR
    S0["Feature Request"]
    S0 -->|1| S1
    S1["Work Order"]
    S1 -->|3 days| S2
    S2["REWQQQQ"]

    %% Add wait times
    S0 -.->|Wait: 5| S1
    S1 -.->|Wait: 23| S2

    %% Add process metrics
    subgraph Metrics
        PT[Process Time: 7 units]
        LT[Lead Time: 35 units]
        FE[Flow Efficiency: 20%]
    end