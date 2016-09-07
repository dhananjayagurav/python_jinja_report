# python_jinja_report
Example of how python and jinja2 can be used to generate a beautiful html reports. This example dumps the report in an 
email and sends it to expected recepients. 

The script does following actions -
  1. Reads report name, sql queries and email ids from a config file. 
  2. Connects to a mysql server and executes the quesries read in step 1
  3. Dumps the mysql output in report template
  4. Attach the report template to email message
  5. Sends the report
  

