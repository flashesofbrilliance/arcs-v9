> DRAFT FOR ZACH. Not sent. Counterpart-facing text once the checks in `08-jargon-map-and-loss-log.md` are done. Nothing here is legal advice; where law or contracts come up, your lawyers decide.

# The translation codex

A legend for the technical words you will hear. Each one gets a plain meaning, a picture to hold, and why it matters to you. If a word is missing, ask, and we will add it.

## The building blocks

| Word | In plain words | Picture | Why it matters to you |
|---|---|---|---|
| **Front end** | The part of the app people see and tap. | The shop window and the shop floor. | Yours already works; the open questions are behind the window. |
| **Back end** | The part people do not see, where information is stored and rules are applied. | The stockroom and the office. | Where private information lives, so it is where most care is needed. |
| **Database** | An organised place where the app keeps its information. | A very tidy filing cabinet. | Supabase plays this role for you. |
| **Lovable and Supabase** | Lovable helps build the app's screens from instructions. Supabase stores the app's information and handles who can log in. | A builder who sketches the shop, and the cabinet inside it. | Each is a separate company with its own rules for what you may put in it. |
| **AI model** | The program that reads a question and writes an answer. | A very well-read assistant who has never met your family. | Alice is built on one. Which one is a decision, not a given. |
| **Prompt** | The written instructions that tell the AI how to behave. | A briefing note. | Alice's voice and her limits live here. |
| **Vendor, provider** | A company whose service you rely on. | A supplier. | Every supplier brings terms and a bill, and switching one can be easy or painful. |
| **API** | A doorway one program uses to ask another for something. | A shop's order window. | Alice reaches the AI model through one. |
| **Lock-in** | When leaving a supplier is costly. | A phone contract with a penalty. | We build so you can switch AI providers without rebuilding. |

## How Alice works

| Word | In plain words | Picture | Why it matters to you |
|---|---|---|---|
| **Token** | A small chunk of text the AI reads or writes. Usage is billed by the chunk. | A taxi meter that counts words instead of miles. | Longer documents and more conversations mean a bigger bill. |
| **Usage cap** | A ceiling on how much AI use is allowed. | A prepaid card with a limit. | Stops a surprise bill. |
| **Retrieval** | Alice looking things up in the vault before answering. | A librarian fetching the right folder first. | It is why uploaded documents affect cost and privacy. |
| **Hallucination** | When an AI states something wrong in a confident voice. | A fluent speaker who has not checked the facts. | Why we test Alice and why every document gets fact-checked, ours included. |
| **Model version, "freezing" it** | Locking Alice to a specific version of the AI so it does not change behaviour under you. | Printing a form and not editing it mid-year. | Keeps results steady and lets you check them. |
| **Redaction** | Hiding private details before something is used or shared. | A black marker over names. | Automatic hiding misses things, so we pair it with a parent review step. |

## Keeping the build safe

| Word | In plain words | Picture | Why it matters to you |
|---|---|---|---|
| **Version control, branch** | A record of every change to the app, with a safe side-copy to try changes before they go live. | Track changes in a document, plus a draft copy. | You can see who changed what and undo a mistake. |
| **Environment (testing, live)** | Separate copies of the app for practising and for real use. | A rehearsal stage and the real stage. | Practice never touches real families' information. |
| **Data placement** | Deciding which kind of information may be kept in which service. | Valuables in the safe, receipts in the drawer. | Services differ in what they are cleared to hold; your lawyers decide. |
| **Evidence trail** | A record showing a safeguard is in place and when it was checked. | Receipts for every safeguard. | Answers "how do you know?" if anyone asks. |
| **Backup and restore test** | A saved copy, and proof that it can be brought back. | A fire drill, not just a fire exit. | A backup nobody has tested is a hope. |
| **Re-platforming** | Moving the app or its information to a different service. | Moving shop. | Only if a service turns out not to be the right home. |

## Who can see what

| Word | In plain words | Picture | Why it matters to you |
|---|---|---|---|
| **Role-based access** | Different people see different things based on who they are. | Keys that open only some doors. | Parents, children and practitioners need different views. |
| **Audit log** | A diary of who did what and when. | A visitor book at the door. | Helps with trust, questions and problems. |
| **Retention** | How long information is kept. | How long a shop keeps receipts. | Kept too long can be a risk; ask your lawyers what is right. |
| **Synthetic data** | Made-up information that looks real. | A rehearsal with actors. | We test with this, never with real families. |
| **Second check at login** | A second proof that it is really you. | A code sent to your phone. | A basic protection for every account. |

## The legal alphabet (for your lawyers, not for us)

| Word | In plain words | Why it matters to you |
|---|---|---|
| **HIPAA** | United States federal privacy rules for certain health information held by certain organisations. | Whether it applies to My Ally LD is for your lawyers. |
| **COPPA** | United States federal rules about collecting information from children online. | Same: your lawyers decide how it applies. |
| **BAA** | A contract between an organisation that handles health information and a service company that handles it for them. | Some AI providers offer one; whether you need one is for your lawyers. |
| **Accessibility standard** | A published set of rules for making a product usable by people with disabilities. | You choose which one to follow, with advice. |

## Working together

| Word | In plain words | Picture | Why it matters to you |
|---|---|---|---|
| **Sprint** | A short push of work with a fixed length. | A sprint in a race, not a marathon. | Each stage ends with something you can check. |
| **Roadmap** | The plan in time order. | A route on a map with stops. | Stage 2 builds it with you. |
| **Dependency** | One thing that must finish before another can start. | You cannot frost a cake that is not baked. | A campaign calendar has them too. |
| **Backlog** | The to-do list, in priority order. | The next items in a shopping basket. | You decide the order. |
| **Definition of done** | A written checklist for what "finished" means. | The brief a campaign is judged against. | Ends arguments about whether something is finished. |
| **First release, thin path** | The smallest version that works from start to finish. | One complete route before the whole map. | Smaller, safer, earlier. |
| **Trial run, spike** | A small time-limited experiment. | A pilot batch. | Learn the cost before committing. |
| **Handoff pack** | Everything we made, in your hands. | The binder you take if you leave the table. | Means you lose nothing if we stop. |

## Money

| Word | In plain words | Picture | Why it matters to you |
|---|---|---|---|
| **Unit economics** | What each family costs you versus what each brings in. | Cost and revenue of one customer. | Kelly's world: it decides whether growth helps or hurts. |
| **Fixed, grows with use, hidden costs** | Costs that stay the same, costs that rise with families, and costs nobody listed. | Rent, ingredients, and the broken oven. | We list all three. |
| **Best, likely, worst case** | Three versions of a number, defined before anyone fills it in. | A forecast with a range. | Prevents wishful thinking. |

## Decisions and honesty

| Word | In plain words | Picture | Why it matters to you |
|---|---|---|---|
| **Decision record** | One page saying what we chose, why, and what would change our minds. | The minutes of a meeting that people actually reread. | Memory fades; the page does not. |
| **"Imagine it failed" exercise** | Picture the project a year from now having failed, and write the story. | A reverse planning session. | Surfaces risks while they are cheap to fix. |
| **Looking back** | Comparing what we set out to do with what happened. | A quarterly review. | Turns every stage into a lesson. |
| **Checkpoint** | A test set in advance that says whether reality matches the plan. | A milestone in a campaign. | Keeps everyone honest without blame. |
| **Predict first, check later** | Writing down what we expect before work starts. | A forecast filed before the quarter. | Lets us see if our judgement is improving. |
| **Fact-check** | Verifying each factual claim against the code or a trusted source. | A copy editor with a red pen. | Applies to every document, ours included. |
| **Shared documents versus shared understanding** | Having the same papers does not mean having the same picture. | Two teams reading one budget two ways. | The reason this engagement exists. |
