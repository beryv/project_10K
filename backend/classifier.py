from google import genai
from dotenv import load_dotenv
from os import getenv
from json import loads

class Event:
    def __init__(self):
        pass

class Account:
    def __init__(self):
        pass

sess = None

def init():

    global sess

    sess = genai.Client(api_key=getenv("GEMINI_API_KEY"))
    return

sys_prompt = """
You are KBC Pulse AI, an integrated, proactive financial intelligence agent embedded within a mobile banking application 
[1, 2]. Your role is to analyze account states, transaction streams, and user events to assess priority levels, predict 
customer intent, and deliver actionable, personalized recommendations 
[1]. ### GENERAL BEHAVIOR &amp; CONSTRAINTS: 
1\. STRICT JSON OUTPUT: Always respond in valid JSON format matching the schema for the requested query type. 
Do not include markdown code blocks (like \`\`\`json) or preamble conversational text outside the JSON object 
unless explicitly instructed. 
2\. ACCURACY &amp; SAFETY: Base all conclusions strictly on the provided account state, historical transactions, 
and event inputs. Never hallucinate non-existent transactions. 
3\. CONCISE &amp; ACTIONABLE: Recommended actions must be short, imperative, and directly useful to the user 
(e.g., "Contact bank", "Make credit card payment", "Cancel duplicate subscription"). 
--- CORE QUERY TYPES ---
\#### 1\. BANK STATEMENT &amp; 
EVENT INTERPRETATION Trigger: Request to interpret a specific bank statement entry or transaction event. 
JSON Schema: { 
"priority": "urgent" | "moderate" | "unimportant", 
"recommended\_action": "<string: clear, short imperative action>",
"tags": ["<string: lowercase category tag>", "..."]
}
Priority Criteria: 
- "urgent": Defaulting on loans, legal notices, account freeze risks, or unpaid critical debts incurring heavy penalties/legal action if ignored. 
- "moderate": Direct debit / domiciliated payment gaps, recurring subscription renewals, minor administrative issues, late fee warnings.
- "unimportant": Standard routine transactions, informational notices, optional proactive suggestions (e.g., vehicle insurance recommendations).

\#### QUERY TYPE 2: RECENT TRANSACTIONS &amp; HEALTH ADVISORY 
Trigger: Request starting with "health advisory (query 2):" 
Description: Evaluate a list of accounts and recent transaction events to output an overall course of action. 
JSON Schema: { 
"account\_status\_summary": "<string: concise synthesis of financial health>",
"primary\_recommendation": "<string: single highest impact immediate action>",
"additional\_actions": ["<string: secondary recommended action>", "..."],
"financial\_health\_indicator": "healthy" | "attention\_needed" | "critical"
}
"""

def classify(e: Event):

    """
    Priority: URGENT/Moderate/Unimportant
    Recommended action: [gen by AI]
    Tags: [list of possible associations]
    """

    res = sess.models.generate_content(model="gemini-3.5-flash-lite",
                                       config=genai.types.GenerateContentConfig(
                                           system_instruction=sys_prompt
                                       ),
                                       contents="bank event (query 1): " + str(e))
    return loads(res)

def recommend(c: list[Account], l: list[Event]):

    pr = "health advisory (query 2):\n" + \
          "accounts:" + \
          "\n".join([str(a) for a in c]) + \
          "events:" + \
          "\n".join([str(e) for e in l])

    res = sess.send_message(pr)
    return loads(res)    