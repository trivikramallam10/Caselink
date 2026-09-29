import re
from difflib import SequenceMatcher
_model=None
def similarity(a,b):
 global _model
 a=(a or "").strip(); b=(b or "").strip()
 if not a or not b:return 0
 if _model is None:
  try:
   from sentence_transformers import SentenceTransformer
   _model=SentenceTransformer("all-MiniLM-L6-v2")
  except Exception: _model=False
 if _model:
  try:
   from sklearn.metrics.pairwise import cosine_similarity
   v=_model.encode([a,b]); return max(0,min(float(cosine_similarity([v[0]],[v[1]])[0][0]),1))
  except Exception: pass
 return SequenceMatcher(None,re.sub(r"\W+"," ",a.lower()),re.sub(r"\W+"," ",b.lower())).ratio()
def find_matches(rows):
 result=[]
 for i in range(len(rows)):
  for j in range(i+1,len(rows)):
   a,b=rows[i],rows[j]; sem=similarity(a["description"],b["description"])
   l1=(a["location"] or "").lower().strip(); l2=(b["location"] or "").lower().strip()
   loc=25 if l1 and l2 and l1==l2 else (15 if l1 and l2 and (l1 in l2 or l2 in l1) else 0)
   date=15 if a["evidence_date"] and a["evidence_date"]==b["evidence_date"] else 0
   desc=sem*60; total=min(100,desc+loc+date)
   if total>=40: result.append({"evidence1":a,"evidence2":b,"score":round(total,2),"description_score":round(desc,2),"location_score":loc,"date_score":date,"semantic_similarity":round(sem*100,2)})
 return sorted(result,key=lambda x:x["score"],reverse=True)
