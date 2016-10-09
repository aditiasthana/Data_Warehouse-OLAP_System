********************************		QUERIES_FINAL.PY		*********************************************

Description:
Contains all queries asked in the project description.

Usage:
Run using python queries_final.py

Just keep giving input as program proceeds IN SINGLE QUOTES to get the results.
for eg:
	Select the query to execute:
	 1. Number of patients for disease
	 2. List type of drugs for disease
	 3. List of mRNA values of probes for disease
	 4. T-Test of expression values for patients with different disease
	 5. F statistics of expression values for patients with different disease
	 6. Average Correlation of expression values for patients with different disease
	 7. Find Informative genes
	 8. Classify patients based on informative genes
	 9. Exit
	Query Number : 1

	Select the field you want to enter
		 1. Disease description
		 2. Disease type
		 3. Disease name
	Choice : 2
	Disease type : 'leukemia'
	Count of Patients with type = leukemia is 27


**Remove any forward zeros
eg: for go_id = 0007154 enter '7154'

** For query 5 when giving multiple disease names please input in single quotes:
eg: 'ALL','AML'



********************************		OLAP WEB APP		*********************************************

Description:
We can perform join, rollup, drilldown, slice and dice OLAP operations using this app.



Installation and Running the app:
1. Install Python 2.7 
2. Install flask using pip install flask
3. Install cx_Oracle (Oracle client for python) using pip install cx_Oracle
*  We need Oracle instant client 12 basic and sdk libraries for this which can be downloaded from Oracle website
4. run app.py using python app.py to start our backend services
5. Open index.html in data mining folder and fill in parameters to perform the respective operations
