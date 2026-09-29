import re
def analyze_statement(s,timeline,evidence):
 text=(s["statement_text"] or "").strip(); low=text.lower(); flags=[]
 uncertain=[x for x in ["maybe","perhaps","probably","possibly","i think","i guess","not sure","don't remember","cannot remember"] if x in low]
 if uncertain: flags.append({"kind":"language","title":"Uncertainty wording","detail":"Found: "+", ".join(uncertain)+". This can reflect ordinary uncertainty."})
 hedge=[x for x in ["approximately","around","roughly","somewhere","sort of","kind of"] if x in low]
 if hedge: flags.append({"kind":"language","title":"Approximation wording","detail":"Found: "+", ".join(hedge)+"."})
 if len(text.split())<10: flags.append({"kind":"language","title":"Short statement","detail":"The statement has fewer than 10 words, so it may contain limited detail."})
 locs=[]
 for x in list(timeline)+list(evidence):
  loc=(x["location"] or "").strip()
  if loc and loc.lower() not in [z.lower() for z in locs]:locs.append(loc)
 found=[x for x in locs if x.lower() in low]
 if found: flags.append({"kind":"context","title":"Recorded location mentioned","detail":"The statement mentions: "+", ".join(found)+"."})
 times=re.findall(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b|\b(?:1[0-2]|0?[1-9])\s?[ap]m\b",low)
 recorded=[x["event_time"] for x in timeline if x["event_time"]]
 if times and recorded: flags.append({"kind":"context","title":"Time references need review","detail":"Statement time(s): "+", ".join(times)+". Recorded event time(s): "+", ".join(recorded)+"."})
 if not flags:flags.append({"kind":"info","title":"No configured indicators detected","detail":"The checks found no configured indicators; this does not establish accuracy."})
 return {"flags":flags,"word_count":len(text.split()),"notice":"These rule-based indicators are for human review only. They are not a credibility score or lie detector."}
