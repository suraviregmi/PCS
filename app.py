from flask import Flask, render_template, url_for, request, redirect 
import os, csv, json
import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests
import sqlite3
import re






from sastodeal import SastoDealScraper
from nepbayScraper import NepbayScraper

from Muncha import MunchaDynamicScraper
from bhatbhateni import BhatbhateniScraper


app = Flask(__name__)

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/home.html')
def home():
	return render_template('home.html')


@app.route('/about.html')
def about():
	return render_template('about.html')

@app.route('/contact.html')
def contact():
	return render_template('contact.html')

@app.route('/another.html', methods=['POST', 'GET'])
def another():
	
	if request.method == "POST":
		c_name = request.form['contacter_name']
		c_email = request.form['contacter_email']
		c_message=request.form['contacter_message']

		conn = sqlite3.connect("test.db")
		curr= conn.cursor()
		curr.execute('''CREATE TABLE IF NOT EXISTS contacter
		(
		name CHAR(255) NOT NULL, 
		email CHAR(255) NOT NULL,
		message CHAR(255) NOT NULL
		)''')
		if c_name:
			curr.execute('''INSERT INTO contacter(name,email,message)
				VALUES(?,?,?)''', [c_name,c_email,c_message]);
			conn.commit()
			return redirect(url_for('thanks'))
	return render_template('another.html')
			
@app.route('/thanks')
def thanks():
	return render_template('thanks.html')

@app.route('/search', methods = ['POST','GET'])
def search():
	
	product_keyword = request.form['Product']
	print(product_keyword)


	#MunchaDynamicScraper(product_keyword)
	#NepbayScraper(product_keyword)
	#SastoDealScraper(product_keyword)
	#BhatbhateniScraper(product_keyword)


	#make the comparison algorithm here
	conn = sqlite3.connect("test.db")
	
	conn.row_factory = sqlite3.Row

	cur = conn.cursor()
	cur.execute("select * from muncha")

	rows = cur.fetchall();

	cur.execute("select *from NepBay")

	rowsNB = cur.fetchall();
	cur.execute("select * from sastodeal")
	rowsSD = cur.fetchall();


	cur.execute("select * from bhatbhateni")
	rowsBB = cur.fetchall();
	return render_template('search.html', rows = rows, rowsNB = rowsNB, rowsSD = rowsSD, rowsBB = rowsBB)




@app.route('/compare', methods = ['POST','GET'])
def compare():
	conn  = sqlite3.connect("test.db")
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	#cur.execute('''select * from muncha natural join NepBay 
	#where muncha.parameter = NepBay.p_NB''')

	#for all 4
	cur.execute("""
		create view if not exists fourSNMB as
		select * from NepBay natural join muncha natural join bhatbhateni  natural join sastodeal
 		where
 		NepBay.p_NB = muncha.parameter
 		and NepBay.p_NB = bhatbhateni.p_BB
 		and muncha.parameter = bhatbhateni.p_BB
 		and NepBay.p_NB = sastodeal.parameter_SD
 		and muncha.parameter = sastodeal.parameter_SD
 		and bhatbhateni.p_BB = sastodeal.parameter_SD""")
	cur.execute("select * from fourSNMB")
	rows_all_four = cur.fetchall();

	# for 3
	cur.execute("""
		create view if not exists threeNMB as
		select * from NepBay natural join muncha natural join bhatbhateni
 		where
 		NepBay.p_NB = muncha.parameter
 		and NepBay.p_NB = bhatbhateni.p_BB
 		and muncha.parameter = bhatbhateni.p_BB""")
	cur.execute("select * from threeNMB")
	rows = cur.fetchall();

	# for muncha and nepbay
	cur.execute("""
		create view if not exists twoMN as
	select * from NepBay natural join muncha
	where NepBay.p_NB = muncha.parameter""")
	cur.execute("select * from twoMN")
	rows2 = cur.fetchall();

	#for nepbay and bhathateni
	cur.execute("""
		create view if not exists twoNB as
		select * from NepBay natural join bhatbhateni
		where NepBay.p_NB = bhatbhateni.p_BB""")
	cur.execute("select * from twoNB")
	rowsNB = cur.fetchall()
	
	
	#for muncha and bhatbheteni
	cur.execute("""
		create view if not exists twoMB as
		select * from muncha natural join bhatbhateni
		where muncha.parameter = bhatbhateni.p_BB""")
	cur.execute("select * from twoMB")
	rowsMB = cur.fetchall()

	#for sastodeal and nepbay
	cur.execute("""
		create view if not exists twoSN as
		select * from sastodeal natural join NepBay
		where sastodeal.parameter_SD = NepBay.p_NB""")
	cur.execute("select * from twoSN")
	rowsSN = cur.fetchall()

	#for sastodeal and muncha
	cur.execute("""
		create view if not exists twoSM as
		select * from sastodeal natural join muncha
		where sastodeal.parameter_SD = muncha.parameter""")
	cur.execute("select * from twoSM")
	rowsSM = cur.fetchall()

	#for sastodeal and bhatbhateni
	cur.execute("""
		create view if not exists twoSB as
		select * from sastodeal natural join bhatbhateni
		where sastodeal.parameter_SD = bhatbhateni.p_BB""")
	cur.execute("select * from twoSB")
	rowsSB = cur.fetchall()



	return render_template('compare.html', rows_all_four = rows_all_four, rows = rows, rows2 = rows2, rowsNB = rowsNB, rowsMB = rowsMB, rowsSN = rowsSN, rowsSM = rowsSM, rowsSB = rowsSB)


if __name__ =='__main__':

	app.run(debug=True)
