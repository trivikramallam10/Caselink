from flask import Flask,render_template,request,redirect,url_for,flash,Response
from database import initialize_database,get_db_connection
from matching import find_matches
from statement_analysis import analyze_statement
import csv,io
app=Flask(__name__); app.secret_key="caselink-demo"; initialize_database()
def case_or_none(cid):
 c=get_db_connection(); r=c.execute("SELECT * FROM cases WHERE id=?",(cid,)).fetchone(); c.close(); return r
@app.route("/")
def dashboard():
 c=get_db_connection(); cases=c.execute("SELECT * FROM cases ORDER BY id DESC").fetchall()
 stats={x:c.execute(f"SELECT COUNT(*) FROM {x}").fetchone()[0] for x in ["cases","suspects","evidence","statements"]}; c.close()
 return render_template("dashboard.html",cases=cases,stats=stats)
@app.route("/create-case",methods=["GET","POST"])
def create_case():
 if request.method=="POST":
  title=request.form.get("title","").strip()
  if not title: flash("Case title is required.","error"); return redirect(url_for("create_case"))
  c=get_db_connection(); n=c.execute("SELECT COUNT(*) FROM cases").fetchone()[0]+1
  c.execute("INSERT INTO cases(case_number,title,description,location,case_date,status) VALUES(?,?,?,?,?,'ACTIVE')",(f"CASE-{n:03d}",title,request.form.get("description",""),request.form.get("location",""),request.form.get("case_date",""))); c.commit(); cid=c.execute("SELECT last_insert_rowid()").fetchone()[0]; c.close()
  return redirect(url_for("case_details", cid=cid))
 return render_template("form.html",title="Create case",subtitle="Create a new investigation workspace",action="Create case",back=url_for("dashboard"),fields=[("title","Case title","text",True),("description","Description","textarea",False),("location","Location","text",False),("case_date","Case date","date",False)])
@app.route("/case/<int:cid>")
def case_details(cid):
 c=get_db_connection(); case=c.execute("SELECT * FROM cases WHERE id=?",(cid,)).fetchone()
 if not case: c.close(); return "Case not found",404
 data={t:c.execute(f"SELECT * FROM {t} WHERE case_id=?"+(" ORDER BY event_date,event_time" if t=="timeline" else " ORDER BY id DESC"),(cid,)).fetchall() for t in ["suspects","evidence","statements","timeline"]}; c.close()
 return render_template("case.html",case=case,**data)
def add_record(cid,table,fields,required):
 case=case_or_none(cid)
 if not case:return "Case not found",404
 if request.method=="POST":
  vals=[request.form.get(k,"").strip() for k,_,_,_ in fields]
  if any(not request.form.get(k,"").strip() for k in required): flash("Please complete the required fields.","error"); return redirect(request.url)
  cols=",".join(["case_id"]+[x[0] for x in fields]); marks=",".join(["?"]*(len(fields)+1))
  c=get_db_connection(); c.execute(f"INSERT INTO {table}({cols}) VALUES({marks})",[cid]+vals); c.commit(); c.close()
  return redirect(url_for("case_details",cid=cid))
 return render_template("form.html",title={"suspects":"Add suspect","evidence":"Add evidence","statements":"Record statement","timeline":"Add timeline event"}[table],subtitle=case["title"],action="Save",back=url_for("case_details",cid=cid),fields=fields)
@app.route("/case/<int:cid>/add-suspect",methods=["GET","POST"])
def add_suspect(cid): return add_record(cid,"suspects",[("name","Name","text",True),("age","Age","number",False),("occupation","Occupation","text",False),("last_seen","Last seen","text",False),("notes","Notes","textarea",False)],["name"])
@app.route("/case/<int:cid>/add-evidence",methods=["GET","POST"])
def add_evidence(cid): return add_record(cid,"evidence",[("title","Evidence title","text",True),("evidence_type","Type (Physical/Digital/Other)","text",False),("description","Description","textarea",False),("location","Location","text",False),("evidence_date","Date","date",False)],["title"])
@app.route("/case/<int:cid>/add-statement",methods=["GET","POST"])
def add_statement(cid): return add_record(cid,"statements",[("person_name","Person name","text",True),("statement_text","Statement text","textarea",True),("statement_date","Statement date","date",False),("location","Reported location","text",False)],["person_name","statement_text"])
@app.route("/case/<int:cid>/add-timeline",methods=["GET","POST"])
def add_timeline(cid): return add_record(cid,"timeline",[("event_title","Event title","text",True),("event_description","Description","textarea",False),("event_date","Event date","date",True),("event_time","Event time","text",False),("location","Location","text",False)],["event_title","event_date"])
@app.route("/case/<int:cid>/statements")
def statements(cid):
 case=case_or_none(cid)
 if not case:return "Case not found",404
 c=get_db_connection(); rows=c.execute("SELECT * FROM statements WHERE case_id=? ORDER BY id DESC",(cid,)).fetchall(); c.close()
 return render_template("statements.html",case=case,statements=rows)
@app.route("/case/<int:cid>/statement/<int:sid>/analyze")
def analyze(cid,sid):
 c=get_db_connection(); case=c.execute("SELECT * FROM cases WHERE id=?",(cid,)).fetchone(); s=c.execute("SELECT * FROM statements WHERE id=? AND case_id=?",(sid,cid)).fetchone(); tl=c.execute("SELECT * FROM timeline WHERE case_id=?",(cid,)).fetchall(); ev=c.execute("SELECT * FROM evidence WHERE case_id=?",(cid,)).fetchall(); c.close()
 if not case or not s:return "Statement or case not found",404
 return render_template("analysis.html",case=case,statement=s,result=analyze_statement(s,tl,ev))
@app.route("/case/<int:cid>/matches")
def matches(cid):
 case=case_or_none(cid)
 if not case:return "Case not found",404
 c=get_db_connection(); ev=c.execute("SELECT * FROM evidence WHERE case_id=?",(cid,)).fetchall(); c.close()
 return render_template("matches.html",case=case,matches=find_matches(ev))
@app.route("/case/<int:cid>/graph")
def graph(cid):
 case=case_or_none(cid)
 if not case:return "Case not found",404
 c=get_db_connection(); items=[]
 for t,label,col in [("suspects","Suspect","name"),("evidence","Evidence","title"),("statements","Statement","person_name"),("timeline","Timeline","event_title")]:
  items += [{"kind":label,"name":r[col]} for r in c.execute(f"SELECT {col} FROM {t} WHERE case_id=?",(cid,))]
 c.close(); return render_template("graph.html",case=case,items=items)
@app.route("/case/<int:cid>/report.csv")
def report(cid):
 case=case_or_none(cid)
 if not case:return "Case not found",404
 out=io.StringIO(); w=csv.writer(out); w.writerow(["Section","ID","Name/Title","Details","Date","Location"])
 c=get_db_connection()
 for t,label,col,detail,date,loc in [("suspects","Suspect","name","notes","","last_seen"),("evidence","Evidence","title","description","evidence_date","location"),("statements","Statement","person_name","statement_text","statement_date","location"),("timeline","Timeline","event_title","event_description","event_date","location")]:
  for r in c.execute(f"SELECT * FROM {t} WHERE case_id=?",(cid,)): w.writerow([label,r["id"],r[col],r[detail] if detail else "",r[date] if date else "",r[loc] if loc else ""])
 c.close(); return Response(out.getvalue(),mimetype="text/csv",headers={"Content-Disposition":f"attachment; filename={case['case_number']}_report.csv"})
if __name__=="__main__": app.run(debug=True)
