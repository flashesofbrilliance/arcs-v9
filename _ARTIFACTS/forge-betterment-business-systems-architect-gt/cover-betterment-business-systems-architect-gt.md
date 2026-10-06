# Cover letter — Betterment · Business Systems Architect, GTM Systems
_Draft. Plain text below is paste-ready. Add any personal availability note by hand._

---

Hi Betterment team,

I run the system, then I build the tool that runs it. That is the short version of why this role fits.

Here is the longer one. Most GTM systems architecture reqs are really a question about who owns the seams: between Salesforce and the data warehouse, between the CRM and the enrichment layer, between what the integration diagram says and what actually flows through it. I have spent two decades on those seams. At Grayscale I led go-to-market for ten SEC/FINRA-regulated products and owned the data contracts, field-mapping logic, and system-of-record boundaries that kept ten systems telling the same story through regulated release gates. At a three-business-unit nonprofit I built the enterprise data layer from nothing, CDP evaluation through Salesforce Lightning modernization, and net-new revenue moved twenty percent because the segmentation finally matched the lifecycle.

A few things I noticed that made me want to write.

Betterment runs three distinct GTM motions: retail, advisor (BAS), and workplace (B@W). That is three sets of stakeholders with different workflows, different data shapes, and different compliance surfaces, all expected to resolve cleanly inside one Salesforce org with HubSpot and Clay in the surrounding stack. The architectural risk is not any single integration; it is the system-of-record boundaries eroding across those motions over time. That is exactly the kind of ambient debt I was hired to find and fix at Grayscale, and the kind I know how to audit before it reaches a stakeholder.

The JD also calls out AI-driven GTM tooling and data enrichment as a forward-looking priority. I built ARCS, an LLM-native decision pipeline on Claude with a live MCP server, and I use it the way a good operator uses any tool: to make enrichment, scoring, and pipeline-visibility work run on its own. I am not applying as an AI engineer. I am applying as the architect who can evaluate Clay and adjacent vendors against real requirements, pressure-test their claims, and bring that tooling into Betterment's workflows without waiting on a platform team.

On me: I do not just draw the architecture diagram. I am in the Salesforce admin panel, the data contract, the integration design review, and the compliance sign-off. SQL, Python, Snowflake, Segment, Salesforce. I have shipped zero to one under SEC/FINRA and HIPAA, which is the part of the job that usually gets underestimated.

Happy to go deep on any of it.

Zach Harris
zachharris.xyz · github.com/flashesofbrilliance

---

## Short version (form-field, ~180 words)

Hi Betterment team,

I run the system, then I build the tool that runs it. GTM systems architecture is really a question about who owns the seams: between Salesforce and the warehouse, between the CRM and the enrichment layer, between the diagram and what actually flows. I have spent two decades on those seams. At Grayscale I led go-to-market for ten SEC/FINRA-regulated products and owned the data contracts and system-of-record boundaries across systems through regulated release gates. At a three-business-unit nonprofit I built the enterprise data layer from nothing through Salesforce Lightning modernization, and net-new revenue moved twenty percent.

Betterment runs three distinct GTM motions: retail, BAS, and B@W. Three stakeholder sets, three data shapes, one Salesforce org with HubSpot and Clay in the surrounding stack. The architectural risk is system-of-record boundaries eroding across those motions over time. That is exactly the kind of ambient debt I know how to find before it reaches a stakeholder.

I also built ARCS, an LLM-native pipeline on Claude with a live MCP server, to make enrichment and scoring run on their own. I am the operator who brings that tooling into your workflows, not an AI engineer.

SQL, Python, Snowflake, Segment, Salesforce. Zero to one under SEC/FINRA and HIPAA.

Zach Harris

---
_Hook: He has owned the exact seam Betterment is hiring for: three-motion GTM architecture inside a regulated financial-services stack, with hands-on AI enrichment tooling already in production._
