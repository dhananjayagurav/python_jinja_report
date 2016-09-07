__author__ = 'dhananjay'

import MySQLdb
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from jinja2 import Environment, FileSystemLoader
import os
import smtplib
import ConfigParser
import ast


class GenerateReport(object):
	def __init__ (self):
		#set report_date for object
		self.report_date = sys.argv[1]		
		
		# Create the root message and fill in the from, to, and subject headers
		self.msgRoot = MIMEMultipart('related')
		self.msgRoot.preamble = 'This is a multi-part message in MIME format.'
		
		# Encapsulate the plain and HTML versions of the message body in an
		# 'alternative' part, so message agents can decide which they want to display.
		self.msgAlternative = MIMEMultipart('alternative')
		self.msgRoot.attach(self.msgAlternative)
		self.msgText = MIMEText('This is the alternative plain text message.')
		self.msgAlternative.attach(self.msgText)


	def querymysql (self, report_nm, sql_qry, server = 'localhost', user = 'admin', passwd = 'admin',database='TestReports'):
		# Open database connection
		db = MySQLdb.connect(server,user,passwd,database)
		# Prepare a cursor object using cursor() method
		cursor = db.cursor()
		# Capture our current directory
		THIS_DIR = os.path.dirname(os.path.abspath(__file__))
		
		# Notice the use of trim_blocks, which greatly helps control whitespace.
		j2_env = Environment(loader=FileSystemLoader(THIS_DIR),trim_blocks=True)
		
		#i = 0
		mystr = ''
		mystr += j2_env.get_template('Header.html').render(report_date=self.report_date)
		try:
			# Execute the SQL command
			for report in sql_qry :
				#print "key " + str(i),report
				s = sql_qry[report]
				#print s
				#print self.report_date
				cursor.execute(s,self.report_date)
				# Fetch all the rows in a list of lists.
				results = cursor.fetchall()
				if (report == 'report1' or report == 'report2'):
					mystr += j2_env.get_template('Test_Report_Template.html').render(report_nm=report_nm,report=report,results=results)
					#i += 1
			mystr += j2_env.get_template('Footer.html').render(report_date=self.report_date)
			#print mystr
		except Exception, e:
			print "Unable to fecth data " + str(e)
		self.msgText = MIMEText(mystr,'html')
		self.msgAlternative.attach(self.msgText)
		#Close the cursor
		cursor.close()
		# Disconnect from server
		db.close()


	def send_mail (self,email_id):
		#Extract the from and to mail id's from dictionary email_id
		strFrom = ''
		strTo = ''
		for e_id in email_id:
			if e_id == 'mail_from':
				strFrom = email_id[e_id]
			elif e_id == 'mail_to':
				strTo = email_id[e_id]
	
		#Add the subject, from, to details to megroot
		self.msgRoot['Subject'] = 'Test Report ' + self.report_date
		self.msgRoot['From'] = strFrom
		self.msgRoot['To'] = strTo
		
		#SMTP Details
		self.smtp = smtplib.SMTP("<smtp server>",<smtp port>)
		self.smtp.starttls()
		self.smtp.login('<smtp username>', '<smtp password>')
		try:
			self.smtp.sendmail(strFrom, strTo, self.msgRoot.as_string())
		except Exception, e:
			print "Unable to send mail " + str(e)
		self.smtp.quit()		


	def read_config (self):
                #Initialise the empty dict for report_type and sql_query
		report_name = {}
		sql_queries = {}
		email_details = {}
		config = ConfigParser.ConfigParser()
		config.read("config.ini")
		sections = config.sections()
		for sec in sections:
			options = config.options(sec)
			for option in options:
				if sec == 'report-name' :
					report_name[option] = config.get(sec,option)
					#print report_name[option]
				elif sec == 'sql-queries' :
					sql_queries[option] = config.get(sec,option)
					#print sql_queries[option]
				elif sec == 'email-details' :
					email_details[option] = config.get(sec,option)
		return report_name, sql_queries, email_details	



gen_report = GenerateReport()
r,s,em = gen_report.read_config()
gen_report.querymysql(r,s)
gen_report.send_mail(em)