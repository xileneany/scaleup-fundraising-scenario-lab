# Industrial Scale-Up Scenario Lab

An interactive decision-support prototype exploring how industrial capacity expansion, supplier-network design and fundraising requirements interact during a biotech scale-up.

**Live app:** [Open the Streamlit application](https://fundraising-scenario.streamlit.app/)

## Why I built this

I built this project as a portfolio case around a challenge that sits at the intersection of strategy, operations and finance: how to translate an industrial expansion plan into supply requirements, capital needs and management decisions.

The case is inspired by MicroHarvest's publicly announced scale-up in Leuna, Germany, including its planned 15,000-tonne annual production capacity and €5.5M public grant.

Public company information is used only as context. Supplier relationships, operating costs, cash balances, revenue assumptions and private financing requirements in the model are synthetic.

## What the model connects

The application links four management questions:

- **Capacity planning:** What does a production target imply for expected output and feedstock requirements?
- **Supply resilience:** Which supplier mix can cover demand while limiting concentration risk?
- **Financial impact:** What working capital and scale-up investment could the operating plan require?
- **Fundraising:** How much additional private capital could be required to protect a minimum cash buffer?

The separate **Founder Recommendation** view translates the model outputs into an executive decision summary.

## Model flow

Production scenario  
→ Feedstock requirement  
→ Supplier allocation  
→ Scale-up investment  
→ Cash runway  
→ Funding requirement  
→ Founder recommendation

## Key features

- Interactive production and supply assumptions
- Supplier scoring and allocation model
- Supplier concentration constraint
- Scale-up investment and working-capital bridge
- 36-month synthetic cash-runway simulation
- 18- and 24-month funding requirement calculations
- Private fundraising scenario comparison
- Executive Founder Recommendation view

## Public context vs. synthetic assumptions

### Public context

The portfolio case uses publicly announced information regarding:

- 15,000 tonnes/year planned production capacity
- Leuna, Germany as the announced industrial site
- €5.5M German public grant
- Molasses as the announced primary feedstock

### Synthetic model inputs

The following are illustrative and should not be interpreted as MicroHarvest company data:

- Supplier identities and economics
- Conversion and utilization assumptions
- Operating expenses
- Revenue and margins
- Starting cash
- CAPEX assumptions beyond explicitly identified public information
- Private fundraising requirements
- Cash runway

## Tech stack

- Python
- Pandas
- Streamlit
- Scenario-based financial modeling
- GitHub

## About the project

Built by Xilene S. as an independent portfolio project focused on strategy, operations, supply planning and fundraising decision support.

This project is not affiliated with MicroHarvest and does not contain confidential or internal company information.

## Repository structure

```text
.
├── app.py
├── pages/
│   └── 2_Founder_Recommendation.py
├── data/
│   ├── suppliers.csv
│   ├── production_assumptions.csv
│   ├── production_scenarios.csv
│   └── financial_assumptions.csv
├── utils/
│   ├── supply_model.py
│   └── financial_model.py
└── requirements.txt


