#!venv/bin/python

import json
import requests
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from urllib2 import *
import simplejson
import cx_Oracle
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

myGlobal = 0

#for groupby enter request parameter as a.name. support for multiple groupby columns. wherecondition
#http://127.0.0.1:5000/join?table1=patient&table2=diagnosis&grpcolumn=a.name&aggfunc=COUNT&wherecondition=b.symptom = 'Sympton of ALL' AND a.p_id = b.p_id&aggcolumn=a.name
@app.route('/join', methods=['GET'])
def join():
	# print(request.args.get('table1'))
	print(request.args)
	table1 = request.args.get('table1', "")
	table2 = request.args.get('table2', "")
	joincondition = request.args.get('joincondition', "")
	wherecondition = request.args.get('wherecondition', "")
	groupbycolumn = request.args.get('grpcolumn', "")
	aggregationfunc = request.args.get('aggfunc', "")
	aggregationcolumn = request.args.get('aggcolumn', "")
	usingcolumn = request.args.get('usingcolumn', "")
	list = []
	columns = []
	global myGlobal
	try:
		db = get_oracle_connection();
		cursor = db.cursor()
		viewname = "join" + str(myGlobal)
		myGlobal += 1
		if not wherecondition and not aggregationcolumn and not groupbycolumn:
			qry = 'create or replace view '+viewname+' as (Select * from '+table1+' full inner join '+table2+'  using ('+usingcolumn+'))'
			print qry
			cursor.execute(qry)
			qry = 'Select * from '+viewname
			cursor.execute(qry)
		elif not aggregationcolumn and not groupbycolumn:
			qry = 'create or replace view '+viewname+' as (Select * from '+table1+' full inner join '+table2+'  using ('+usingcolumn+') where '+wherecondition+')'
			print qry
			cursor.execute(qry)
			qry = 'Select * from '+viewname
			cursor.execute(qry)
		elif groupbycolumn is not None and not wherecondition:
			qry = 'create or replace view '+viewname+' as (Select '+groupbycolumn+', '+ aggregationfunc +'('+aggregationcolumn+') as ' + aggregationcolumn+'_1 from '+table1+' full inner join '+table2+' using (' +usingcolumn+') group by '+ groupbycolumn+')'
			print qry
			cursor.execute(qry)
			qry = 'Select * from '+viewname
			cursor.execute(qry)
		elif groupbycolumn is not None and wherecondition is not None:
			qry = 'create or replace view '+viewname+' as (Select '+groupbycolumn+', '+ aggregationfunc +'('+aggregationcolumn+') as ' + aggregationcolumn+'_1 from '+table1+' full inner join '+table2+' using ('+ usingcolumn +') where ' +wherecondition+' group by '+ groupbycolumn+')'
			print qry
			cursor.execute(qry)
			qry = 'Select * from '+viewname
			cursor.execute(qry)
		columns = [i[0] for i in cursor.description]
		print columns
		for row in cursor:
			list.append(row)
	except Exception as e:
		print e
		abort(404);
	return jsonify({'tablename':viewname,'columns':columns,'rows':list})
	
#http://127.0.0.1:5000/rollup?rollupcolumn=patientid,disease,sampleid&aggfunc=avg&aggcolumn=exp&tablename=dataset	
#http://127.0.0.1:5000/rollup?rollupcolumn=uid1&aggfunc=stats_t_test_indep&aggcolumn=diseasecat,exp&tablename=persongene1
@app.route('/rollup', methods=['GET'])
def rollup():
	tablename = request.args.get('tablename',"")
	rollupcolumn = request.args.get('rollupcolumn',"")
	aggcolumn = request.args.get('aggcolumn',"")
	aggfunction = request.args.get('aggfunc',"")
	list = []
	columns = []
	global myGlobal
	try:
		db = get_oracle_connection();
		cursor = db.cursor()
		viewname = "rollup" + str(myGlobal)
		myGlobal += 1
		qry = 'create or replace view '+viewname+' as (select '+ rollupcolumn +','+aggfunction +'(' + aggcolumn + ') as '+aggcolumn+'_1 from '+tablename+' group by '+ rollupcolumn+')'
		cursor.execute(qry)
		print qry
		qry = 'select * from '+viewname
		cursor.execute(qry)
		columns = [i[0] for i in cursor.description]
		print columns
		for row in cursor:
			list.append(row)
	except Exception as e:
		print e
		abort(404);
	return jsonify({'tablename':viewname,'columns':columns,'rows':list})

#http://127.0.0.1:5000/slice?tablename=dataset&slicecolumn=disease&slicevalue=AML	
@app.route('/slice', methods=['GET'])
def slice():
	tablename = request.args.get('tablename',"")
	slicecolumn = request.args.get('slicecolumn',"")
	slicevalue = request.args.get('slicevalue',"") 
	list = []
	columns = []
	global myGlobal
	try:
		db = get_oracle_connection();
		cursor = db.cursor()
		viewname = "slice" + str(myGlobal)
		myGlobal += 1
		qry = "create or replace view "+viewname+" as (Select * from "+tablename+" where "+slicecolumn+" = '"+ slicevalue +"')" 
		cursor.execute(qry)
		print qry
		qry = 'select * from '+viewname
		cursor.execute(qry)
		columns = [i[0] for i in cursor.description]
		print columns
		for row in cursor:
			list.append(row)
	except Exception as e:
		print e
		abort(404);
	return jsonify({'tablename':viewname,'columns':columns,'rows':list})
		
#http://127.0.0.1:5000/dice?tablename=dataset&dicecondition=disease='AML' AND patientid <> '79777' AND sampleid <> '973218'
@app.route('/dice', methods=['GET'])
def dice():
	tablename = request.args.get('tablename',"")
	dicecondition = request.args.get('dicecondition',"")
	list = []
	columns = []
	global myGlobal
	try:
		db = get_oracle_connection();
		cursor = db.cursor()
		viewname = "dice" + str(myGlobal)
		myGlobal += 1
		qry = "create or replace view "+viewname+" as (Select * from "+tablename+" where "+dicecondition+")" 
		print qry
		cursor.execute(qry)
		qry = 'select * from '+viewname
		cursor.execute(qry)
		columns = [i[0] for i in cursor.description]
		print columns
		for row in cursor:
			list.append(row)
	except Exception as e:
		print e
		abort(404);
	return jsonify({'tablename':viewname,'columns':columns,'rows':list})

#
#create or replace view temp1 as (select * from clinical_sample full inner join diagnosis using(p_id));
#select * from temp1;
#create or replace view temp2 as (select * from temp1 full inner join disease using(ds_id));
#select * from temp2;
#create or replace view temp3 as (select name,type,count(amount) as amount from temp2 group by name,type);
#select * from temp3;
#
#create or replace view temp4 as (c);
#select * from temp4;
#select p_id,name,type,amount from temp2 where name in (select name from temp3) and type in (select type #from temp3);
#	
@app.route('/drilldown', methods=['GET'])
def drilldown():
	basetable = request.args.get('basetable',"")
	drilldowntable = request.args.get('drilldowntable',"")
	drilldownfromcolumn = request.args.get('drilldownfromcolumn',"")
	drilldowntocolumn = request.args.get('drilldowntocolumn',"")
	#aggcolumn = request.args.get('aggcolumn')
	#aggfunction = request.args.get('aggfunc')
	#groupbycolumn = request.args.get('groupbycolumn')
	list = []
	columns = []
	global myGlobal
	try:
		db = get_oracle_connection();
		cursor = db.cursor()
		viewname = "drilldown" + str(myGlobal)
		myGlobal += 1
		qry = 'select * from '+drilldowntable
		print qry
		cursor.execute(qry)
		drillcolumns = [i[0] for i in cursor.description]
		drilltocolumns = []
		for x in drillcolumns:
			if '_1' in x:
				drillcolumns.remove(x)
				strcol = x.replace("_1","")
				drilltocolumns.append(strcol)
		drilltocolumns.append(drilldowntocolumn)
		for x in drillcolumns:
			if drilldownfromcolumn.lower() <> x.lower():
				print drilldownfromcolumn.lower()  + " comparing " + x.lower()
				drilltocolumns.append(x)
		selectstr = ""
		for x in drilltocolumns:
			selectstr += x + ","
		selectstr = selectstr[0:len(selectstr)-1]
		wherestr = " where "
		count = 0
		for x in drillcolumns:
			xstr = x + " in (select " + x +" from " + drilldowntable +')'
			if count == 0:
				wherestr += xstr
			else:
				wherestr += " and " + xstr
			count += 1
		qry = "create or replace view "+viewname+" as (select " + selectstr + " from " + basetable + " " + wherestr + ')'
		print qry
		cursor.execute(qry)
		qry = 'select * from '+viewname
		cursor.execute(qry)
		columns = [i[0] for i in cursor.description]
		print columns
		for row in cursor:
			list.append(row)
	except Exception as e:
		print e
		abort(404);
	return jsonify({'tablename':viewname,'columns':columns,'rows':list})
		
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
	
def get_oracle_connection():
	ip = 'aos.acsu.buffalo.edu'
	port = 1521
	SID = 'aos.buffalo.edu'
	dsn_tns = cx_Oracle.makedsn(ip, port, SID).replace('SID','SERVICE_NAME')
	db = cx_Oracle.connect('shaleenm', 'cse562', dsn_tns)
	return db

if __name__ == '__main__':
    app.run(debug=True)