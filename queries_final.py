import json
import requests
import simplejson
import cx_Oracle

def get_oracle_connection():
	ip = 'aos.acsu.buffalo.edu'
	port = 1521
	SID = 'aos.buffalo.edu'
	dsn_tns = cx_Oracle.makedsn(ip, port, SID).replace('SID','SERVICE_NAME')
	db = cx_Oracle.connect('shaleenm', 'cse562', dsn_tns)
	return db

def patients_with_disease(field, disease, cursor):
	try:
		if field == 'name':
			cursor.execute("SELECT COUNT(p_id) as Patient_no FROM diagnosis where ds_id IN (SELECT ds_id FROM disease where name = "+"'"+disease+"'"+")")
		elif field == 'description':
			cursor.execute("SELECT COUNT(p_id) FROM diagnosis where ds_id IN (SELECT ds_id FROM disease where description = "+"'"+disease+"'"+")")
		elif field == 'type':
			cursor.execute("SELECT COUNT(p_id) FROM diagnosis where ds_id IN (SELECT ds_id FROM disease where type = "+"'"+disease+"'"+")")
		
		res = cursor.fetchall()
		print "Count of Patients with "+field + " = "+ disease + " is " + str(res[0][0])
	except Exception as e:
		print e


def type_of_drugs(field,disease, cursor):
	try:
		if field == 'name':
			cursor.execute("SELECT DISTINCT(type) as DRUG_TYPE FROM DRUG WHERE dr_id IN (SELECT dr_id FROM Drug_use WHERE p_id IN (SELECT p_id FROM diagnosis where ds_id IN (SELECT ds_id FROM disease where name = "+"'"+disease+"'"+")))")
		elif field == 'description':
			cursor.execute("SELECT DISTINCT(type) as DRUG_TYPE FROM DRUG WHERE dr_id IN (SELECT dr_id FROM Drug_use WHERE p_id IN (SELECT p_id FROM diagnosis where ds_id IN (SELECT ds_id FROM disease where description = "+"'"+disease+"'"+")))")
		elif field == 'type':
			cursor.execute("SELECT DISTINCT(type) as DRUG_TYPE FROM DRUG WHERE dr_id IN (SELECT dr_id FROM Drug_use WHERE p_id IN (SELECT p_id FROM diagnosis where ds_id IN (SELECT ds_id FROM disease where type = "+"'"+disease+"'"+")))")

		res = cursor.fetchall()
		print "Following Drugs were applied to patients with "+field + " = "+ disease
		for val in res:
			print val[0]
	except Exception as e:
		print e

def list_mrna_values(disease,luster_id , measure_unit_id , cursor):
	try:
		query = '''SELECT s.s_id as Sample_id, m.mu_id as measure_unit_id, m.E_ID as Experiment_id, m.Exp as EXP
						FROM microarray_fact m, clinical_sample s, diagnosis d, disease di
						WHERE m.mu_id= '''+"'"+measure_unit_id+''''
						AND m.s_id = s.s_id 
						AND s.p_id = d.p_id 
						AND d.ds_id = di.ds_id
						AND m.pb_id IN ( SELECT DISTINCT(pb_id) FROM PROBE WHERE UID1 IN (SELECT DISTINCT(UID1) FROM gene_cluster WHERE cl_id = '''+"'"+cluster_id+"'"+'''))
						and di.NAME = '''+"'"+disease+"'"
		cursor.execute(query)

		print "List of mRNA Values"
		res = cursor.fetchall()
		print "Number of records returned : "+ str(len(res))
		print ('Sample_id', 'measure_unit_id' , 'Experiment_id', 'EXP')
		for val in res:
			print val
	except Exception as e:
		print e

def t_test( go_id, disease, cursor):
	try:
		query = '''Create or Replace View temp_t_test1 as
							SELECT di.NAME as disease,  
								   m.exp as exp
							FROM   microarray_fact m, 
								   clinical_sample s, 
								   diagnosis d, 
								   disease di 
							WHERE  m.s_id = s.s_id 
								   AND s.p_id = d.p_id 
								   AND d.ds_id = di.ds_id 
								   AND m.pb_id IN (SELECT DISTINCT( pb_id ) 
												   FROM   probe 
												   WHERE  uid1 IN (SELECT DISTINCT( uid1 ) 
																   FROM   go_annotation 
																   WHERE  go_id ='''+ "'"+go_id + "'))"
		cursor.execute(query)
		query = '''Create or replace view temp_t_test11 as
							select 'GroupA' as grp,
									EXP
							From temp_t_test1
							where DISEASE = '''+ "'"+disease+ "'"+'''
						UNION ALL
							select 'GroupB' as grp,
									EXP
							From temp_t_test1
							where DISEASE <> '''+ "'"+disease+ "'"
		cursor.execute(query)
		cursor.execute("SELECT STATS_T_TEST_INDEP(grp, exp, 'STATISTIC', 'GroupA') T_OBSERVED ,STATS_T_TEST_INDEP(grp, exp) P_VALUE FROM temp_t_test11")
		res = cursor.fetchall()
		print 'T_OBSERVED value is '+ str(res[0][0])
		print 'P_VALUE is '+ str(res[0][1])
	except Exception as e:
		print e

def f_test(go_id, cursor, diseases):
	try:
		query = '''Create or Replace View temp_f_test1 as
							SELECT di.NAME as disease,  
								   m.exp as exp
							FROM   microarray_fact m, 
								   clinical_sample s, 
								   diagnosis d, 
								   disease di 
							WHERE  m.s_id = s.s_id 
								   AND s.p_id = d.p_id 
								   AND d.ds_id = di.ds_id 
								   AND m.pb_id IN (SELECT DISTINCT( pb_id ) 
												   FROM   probe 
												   WHERE  uid1 IN (SELECT DISTINCT( uid1 ) 
																   FROM   go_annotation 
																   WHERE  go_id = '''+ "'"+go_id+ "'))"
		cursor.execute(query)

		strDisease = ""
		for var in diseases:
			strDisease = strDisease +",'"+ var.strip() + "'"
		strDisease = strDisease[1:]
		
		cursor.execute('''Create or replace view temp_f_test2 as
							select disease,
									EXP
							From temp_f_test1
							where disease IN ('''+ strDisease+ " )")

		cursor.execute("SELECT STATS_ONE_WAY_ANOVA(Disease, exp, 'F_RATIO') F_OBSERVED FROM temp_f_test2")
		res = cursor.fetchall()
		print 'F_OBSERVED value is '+ str(res[0][0])
	except Exception as e:
		print e

def avg_corr(go_id, disease1, disease2, cursor):
	try:
		query = '''CREATE OR replace VIEW temp_corr_1 
							AS 
							  SELECT s.p_id  AS patientid, 
									 p.uid1  AS UID1, 
									 di.name AS disease, 
									 s.s_id as sampleID,
									 p.pb_id as probeid,
									 m.exp   AS exp 
							  FROM   microarray_fact m, 
									 clinical_sample s, 
									 diagnosis d, 
									 disease di, 
									 probe p, 
									 go_annotation g 
							  WHERE  m.s_id = s.s_id 
									 AND s.p_id = d.p_id 
									 AND d.ds_id = di.ds_id 
									 AND m.pb_id = p.pb_id 
									 AND p.uid1 = g.uid1 
									 AND g.go_id = '''+ "'"+go_id+ "'"+'''
									 AND di.name IN ('''+ "'"+ disease1+ "','"+ disease2+ "')"
		cursor.execute(query)

		query = '''create or replace view temp_corr_2
							as
							select d1.patientid as pid1, d1.exp as exp1, d2.patientid as pid2, d2.exp as exp2, CORR(d1.exp ,d2.exp) over (partition by d1.patientid, d2.patientid) as CORR
							from temp_corr_1 d1, temp_corr_1 d2
							where d1.disease = '''+ "'"+disease1+ "'"+'''
							and d2.disease = '''+ "'"+disease2+ "'"+'''
							and d1.patientid <> d2.patientid
							and d1.PROBEID = d2.PROBEID
							order by d1.patientid , d2.patientid'''
		cursor.execute(query)

		cursor.execute("select avg(corr) as CORRELATION from temp_corr_2")
		res = cursor.fetchall()
		print 'Average Correlation between patients of '+disease1+' and '+disease2 +' is '+str(res[0][0])
	except Exception as e:
		print e

def get_informative_genes(disease, cursor):
	try:
		cursor.execute('''Create or Replace view patient_gene_dataset
						as(
						select c.p_id as patientID, g.UID1 as UID1,  ds.NAME as disease , m.exp as EXP
						from Gene g, Probe p , MicroArray_Fact m , Clinical_sample c, Diagnosis d, disease ds
						where g.UID1 = p.UID1
						and p.pb_id = m.pb_id
						and m.s_id = c.s_id
						and c.p_id = d.P_ID
						and d.ds_id = ds.ds_id)''')
		
		cursor.execute('''Create or replace view patient_gene_dataset1 
							as
							select 'GroupA' as grp,
									EXP,
									UID1
							From patient_gene_dataset
							where DISEASE = '''+ "'"+disease+"'"+'''
						UNION ALL
							select 'GroupB' as grp,
									EXP,
									UID1
							From patient_gene_dataset
							where DISEASE <> '''+ "'"+disease+"'")
		
		cursor.execute('''create or replace view patient_gene_dataset2
						as(
						select UID1,
						STATS_T_TEST_INDEP(grp , exp, 'STATISTIC' , 'GroupA') T_observed,
						STATS_T_TEST_INDEP(grp , exp) two_sided_p_value
						from patient_gene_dataset1
						Group by UID1)''')
		
		cursor.execute('''Create or replace view info_gene
						as(
						select UID1
						from patient_gene_dataset2
						where two_sided_p_value < 0.01)''')

		cursor.execute('''select UID1
						from patient_gene_dataset2
						where two_sided_p_value < 0.01''')

		res = cursor.fetchall()
		print 'Informative Genes for '+ disease+ ' are Following'
		for val in res:
			print val[0]
	except Exception as e:
		print e

def classify_patient(patient, disease,cursor):
	try:
		get_informative_genes(disease , cursor)
		
		cursor.execute('''Create or replace view test_group_a
							as
							select p.patientid , CORR(p.exp , t.exp) as CORR
							from patient_gene_dataset p , (select UID1 as UID1 , '''+patient+''' as exp from test_samples) t
							where p.UID1 = t.UID1
							and p.UID1 in (select UID1 from info_gene)
							and p.disease = '''+"'"+disease+"'"+'''
							group by p.patientid''')

		cursor.execute('''Create or replace view test_group_b
							as
							select p.patientid , CORR(p.exp , t.exp) as CORR
							from patient_gene_dataset p , (select UID1 as UID1, '''+patient+''' as exp from test_samples) t
							where p.UID1 = t.UID1
							and p.UID1 in (select UID1 from info_gene)
							and p.disease <> '''+"'"+disease+"'"+'''
							group by p.patientid''')

		cursor.execute('''Select STATS_T_TEST_INDEP(Grp , CORR) p_value
							from (
								  select 'GroupA' as grp, CORR
								  from TEST_GROUP_A
							  union ALL
								  select 'GroupB' as grp , CORR
								  from test_group_b)''')

		res = cursor.fetchall()
		if res[0][0] < 0.01 :
			print 'Prediction : ' + patient + ' have '+disease
		else:
			print 'Prediction : ' + patient + ' do not have '+disease
	except Exception as e:
		print e
		
if __name__ == '__main__':
	db = get_oracle_connection()
	try:
		db = get_oracle_connection();
		cursor = db.cursor()
		flag = True
		while(flag):
			print '\nSelect the query to execute:'
			print '\t 1. Number of patients for disease'
			print '\t 2. List type of drugs for disease'
			print '\t 3. List of mRNA values of probes for disease'
			print '\t 4. T-Test of expression values for patients with different disease'
			print '\t 5. F statistics of expression values for patients with different disease'
			print '\t 6. Average Correlation of expression values for patients with different disease'
			print '\t 7. Find Informative genes'
			print '\t 8. Classify patients based on informative genes'
			print '\t 9. Exit'
			x = input('Query Number : ');
			if x == 1:
				print '\nSelect the field you want to enter'
				print '\t 1. Disease description'
				print '\t 2. Disease type'
				print '\t 3. Disease name'
				y = input('Choice : ');
				if y == 1:
					disease = input('Disease description : ')
					patients_with_disease('description', disease, cursor)
				elif y == 2:
					disease = input('Disease type : ')
					patients_with_disease('type', disease, cursor)
				elif y == 3:
					disease = input('Disease Name : ')
					patients_with_disease('name', disease, cursor)
				else :
					print 'Wrong choice'
			elif x == 2:
				print '\nSelect the field you want to enter'
				print '\t 1. Disease description'
				print '\t 2. Disease type'
				print '\t 3. Disease name'
				y = input('Choice : ');
				if y == 1:
					disease = input('Disease Description : ')
					type_of_drugs('description', disease, cursor)
				elif y == 2:
					disease = input('Disease Type : ')
					type_of_drugs('type', disease, cursor)
				elif y == 3:
					disease = input('Disease Name : ')
					type_of_drugs('name', disease, cursor)
				else :
					print 'Wrong choice'
			elif x == 3:
				cluster_id = input('Enter the cluster id : ')
				measure_unit_id = input('Enter the measure unit id : ')
				disease = input('Disease Name : ')
				list_mrna_values(disease,cluster_id , measure_unit_id , cursor)
			elif x == 4:
				go_id = input('Enter the go id : ')
				disease = input('Enter the disease name : ')
				t_test( go_id, disease, cursor)
			elif x == 5:
				go_id = input('Enter the go id : ')
				disease = input('Enter the disease names seperated by comma : ')
				f_test( go_id, cursor, disease)
			elif x == 6:
				go_id = input('Enter the go id : ')
				disease1 = input('Enter the disease1 name : ')
				disease2 = input('Enter the disease2 name : ')
				avg_corr(go_id, disease1, disease2, cursor)
			elif x == 7:
				disease = input('Enter the disease name : ')
				get_informative_genes(disease, cursor)
			elif x == 8:
				disease = input('Enter the disease name : ')
				patient = input('Enter the patient name : ')
				classify_patient(patient, disease,cursor)
			elif x == 9:
				flag = False
			else :
				print 'Invalid Query Number.'
		cursor.close()
		db.close()
	except Exception as e:
		print e
