# !/usr/bin/env python3.8
# -*- coding: utf-8 -*-

from decimal import Decimal
from datetime import datetime, date, timedelta

import mysql.connector
from mysql.connector.errors import Error
from mysql.connector import errorcode

# Importing the os and fnmatch library
import os, fnmatch

# import for database conversion
import time
import datetime
from datetime import datetime

import sys, getopt

# file rename
import os

# for search within the result-table
import re

def extract(line, starttag, endtag):
    start = line.find(starttag)
    end = line.find(endtag)
    if (start != -1) and (end > start):
      date = line[start+len(starttag): end]
      return date
    return ""

def guess_category(title):
    searchObj = re.search( r'.*[lL]inux.*', title)
    if searchObj:
        return "Linux"
    searchObj = re.search( r'.*[wW]in.*', title)
    if searchObj:
        return "Windows"
    return "Unknown"

def create_result_entry(line, result):
    if (result['name']==""):
        # check on headline
        # <td id="summary-d1e1314" class="group  sub0">1 <a href="#checklist-d1e1314">Initial Setup</a></td>
        searchObj = re.search( r'<td id=\"summary-[a-z0-9]+\" class=\"group  sub([0-9])\">([0-9\.]+) <a href="#checklist-([a-z0-9]+)\">(.*)</a></td>', line)
        if searchObj:
            print("search --> searchObj.group() : ", searchObj.group())
            result['name'] = searchObj.group(3)
            result['headline'] = searchObj.group(4)
            result['layer'] = searchObj.group(1)
            result['position_in_benchmark'] = searchObj.group(2)
            result['line_counter'] = 0
        else:
            print("No headline found!!")
    else:
        # check on attributes
        # <td class="numeric  sub0">16</td>
        searchObj = re.search( r'<td class=\"numeric  sub[0-9]+\">([0-9.]+)[%]?</td>', line)
        if searchObj:
            print("search --> searchObj.group() : ", searchObj.group())
            result['line_counter'] = result['line_counter'] + 1
            if result['line_counter']==8:
                result['percent'] = searchObj.group(1)
            if result['line_counter']==6:
                result['score'] = searchObj.group(1)
        else:
            print("No attribute found!!")
    return result
     
def read_report(file): 
    # reads one sort of html report into our datastructur
    title = ""
    target = ""
    level = ""
    testtime = ""
    summary =-1
    tbody =-1
    result_entry = {'id': "", 'name': "", 'headline': "", 'score': "", 'percent': "", 'line_counter':0, 'layer':"", 'position_in_benchmark':""}
    result_list = []
    test_result = {'title': "", 'category': "", 'time': "", 'level': "", 'target': "0.0.0.0", 'results': []}
    
    try:
        fh = open(file, "r")
    except IOError:
        print("Error: can\'t find file or read from it")
    else:
        
        for line in fh:
            if not testtime:
                #  <meta name="date" content="2020-12-30T21:42:12.467Z"></meta>
                testtime=extract(line,"<meta name=\"date\" content=\"", "\"></meta>")
                if testtime:
                    print("Testtime found:" + testtime)
                    if len(testtime)<24:
                        #  sometimes Assessor creates "2021-03-07T08:58:00.33Z"
                        #  which is not the ISO format
                        replaced = re.sub('\.(??)Z', '\.\\10Z', testtime)
                        print("Testtime replaced by:" + replaced)
                        testtime = replaced
                    test_result['time']=testtime
                    continue;
            if not title:
                #  <title>Benchmark Result xccdf_org.cisecurity.benchmarks_testresult_1.0.0.1_CIS_Amazon_Linux_2_Benchmark</title>
                title=extract(line, "<title>Benchmark Result xccdf_org.cisecurity.benchmarks_testresult_", "</title>")
                if title:
                    print("Title found:" + title)
                    test_result['title']=title
                    test_result['category']=guess_category(title)
                    continue;
            if not target:
                #<li>Target IP Address: 127.0.0.1</li>
                #<h1>for ip-10-0-21-228.eu-central-1.compute.internal</h1>
                #target=extract(line,"<li>Target IP Address: ", "</li>")
                target=extract(line,"<h1>for ", "</h1>")
                if target:
                    print("Target found:" + target)
                    test_result['target']=target
                    continue;
            if not level:
                # <li>Level 1</li>
                level=extract(line,"<li>Level ", "</li>")
                if level:
                    print("Level found:" + level)
                    test_result['level']=level
                    continue;
            if (summary==-1):    
                # <h2 class="sectionTitle">Summary</h2>
                summary=line.find("<h2 class=\"sectionTitle\">Summary</h2>")
                if (summary==-1):    
                    continue;
            if (tbody==-1):    
                tbody=line.find("<tbody>")
                if (tbody==-1):    
                    continue;
            else:
                # start of result-entry
                if line.find("<tr>")!=-1:
                    result_entry = {'id': "", 'name': "", 'headline': "", 'score': "", 'percent':"", 'line_counter':0, 'layer':"", 'position_in_benchmark':"" }
                    continue;
                # result-entry is complete
                if (result_entry['name']) and (line.find("</tr>")!=-1):
                    print("End of ", result_entry['name'])
                    result_list.append(result_entry)
                    continue;
                # end of summary
                if line.find("<th class=\"group\" align=\"right\">Total</th>")!=-1:
                    print("End of summary.")

                    # read next 6 lines to get the total score
                    i = 6
                    for summary_line in fh:
                        i-=1
                        print("Checking summary line:", summary_line)
                        if i == 0:
                            main_score=extract(summary_line,"<td class=\"numeric bold\">", "</td>")
                            print("Score:", main_score)
                            test_result['score'] = main_score
                            break;
                        
                    #result should now be complete
                    test_result['results']=result_list
                    store(test_result)
                    break;
                # add line to current result_entry
                result_entry= create_result_entry(line, result_entry)
                
        if not title:
            print("Title not found in:" + file)    
    try:
        os.rename( file, file + "imp" )
    except IOError:
        print("Error: can\'t rename file")

def import_reports(path): 
 
    # List to store filenames 
    file_list = []
    print("List of reports in the directory:")
    for path, folders, files in os.walk(path):
        for file in files:
            if fnmatch.fnmatch(file, '*.html'):
                file_list.append(os.path.join(path, file))
                
    # Loop to print each filename separately
    for filename in file_list:
        print(filename)
        read_report(filename)

def find_benchmark(test_result):
    # locates database id of appropriate benchmark in internal data structure

    id_benchmark = -1
    global db_benchmarks # {'title+level': "benchmark_id"}

    key = test_result['title'] + test_result['level']
    if db_benchmarks:
        if key in db_benchmarks:
            id_benchmark = db_benchmarks[key]
        
    return id_benchmark;

def find_testname(id_benchmark, result_entry):
    # locates database id of appropriate testname in internal data structure

    id_testname = -1
    global db_testnames #  {'id_benchmark+testname': "testname_id"}

    key = str(id_benchmark) + result_entry['name']
    if db_testnames:
        if key in db_testnames:
            id_testname = db_testnames[key]
        
    return id_testname;

    
def store(test_result):
    global host
    global dbname
    global dbuser
    global dbpwd
    
    global db_benchmarks
    global db_testnames

    category_id = -1 # stored in t_systemtype

    cnx = mysql.connector.connect(user=dbuser, password=dbpwd, host=host, database=dbname)

    # Get two buffered cursors
    curA = cnx.cursor(buffered=True)
    curB = cnx.cursor(buffered=True)
    curC = cnx.cursor(buffered=True)
    curD = cnx.cursor(buffered=True)
    curE = cnx.cursor(buffered=True)
    curF = cnx.cursor(buffered=True)
    curG = cnx.cursor(buffered=True)

    # check if t_benchmark was tested before, insert benchmark
    id_benchmark = find_benchmark(test_result)
    if (id_benchmark == -1):
        print("Benchmark seems to be new.")
        
        # check if t_systemtype was tested before, insert system-type
        query_system_type = (
            "SELECT id FROM t_systemtype "
            "WHERE name = %s")

        try:
            curA.execute(query_system_type, (test_result['category'],))
            row = curA.fetchone()
            if curA.rowcount>0:
                category_id=row[0]
            else:
                #insert t_systemtype
                insert_systemtype = (
                    "INSERT INTO t_systemtype (name) "
                    "VALUES (%s)")
                curB.execute(insert_systemtype,(test_result['category'],))
                category_id = curB.lastrowid
                
            # insert t_benchmark
            insert_benchmark = (
                "INSERT INTO t_benchmark (name, level, t_systemtype_id) "
                "VALUES (%s, %s, %s)")
            curC.execute(insert_benchmark,(test_result['title'], test_result['level'], category_id))
            
            id_benchmark = curC.lastrowid
            print("Inserted Benchmark with: ", id_benchmark, " title:",test_result['title']," level:",test_result['level'] )
            key = test_result['title'] + test_result['level']
            db_benchmarks[key]=id_benchmark
                
            # insert t_testnames
            for result_entry in test_result['results']:
                insert_testname = (
                    "INSERT INTO t_testname (name, layer, position_in_benchmark, headline, t_benchmark_id) "
                    "VALUES (%s, %s, %s, %s, %s)")
                curD.execute(insert_testname,(result_entry['name'], result_entry['layer'], result_entry['position_in_benchmark'], result_entry['headline'], id_benchmark))
                print("t_testname stored.")
                id_testname = curD.lastrowid
                key = str(id_benchmark) + result_entry['name']
                db_testnames[key]=id_testname
                
            # Commit the changes
            cnx.commit()
        except mysql.connector.Error as e:
            print('Exception during benchmark storage:', sys.exc_info()[0])
            print("Error code:", e.errno)        # error number
            print("SQLSTATE value:", e.sqlstate) # SQLSTATE value
            print("Error message:", e.msg)       # error message
            print("Error:", e)                   # errno, sqlstate, msg values
            s = str(e)
            print("Error:", s)                   # errno, sqlstate, msg values
            # Rollback in case there is any error
            cnx.rollback()
            cnx.close()
            return

    try:
        # insert t_benchresult
        insert_benchresult = (
            "INSERT INTO t_benchresult (score, executed, target, t_benchmark_id) "
                    "VALUES (%s, %s, %s, %s)")
        #2021-02-14T21:25:19.307Z
        timestamp = datetime.fromisoformat(test_result['time'].replace('Z', '+00:00'))
        print("Insert Benchmark ", id_benchmark, " with score:",test_result['score']," and ",timestamp)
        curE.execute(insert_benchresult,(float(test_result['score']), timestamp, test_result['target'], id_benchmark))
        id_benchresult = curE.lastrowid        
        
        for result_entry in test_result['results']:
        
            # check if t_testname were tested before, insert testnames
            id_testname = find_testname(id_benchmark, result_entry)
            if (id_testname == -1):
                # insert t_testname
                insert_testname = (
                    "INSERT INTO t_testname (name, layer, position_in_benchmark, headline, t_benchmark_id) "
                    "VALUES (%s, %s, %s, %s, %s)")
                print("Insert testname:", id_benchmark, result_entry['name'])
                curF.execute(insert_testname,(result_entry['name'], result_entry['layer'], result_entry['position_in_benchmark'], result_entry['headline'], id_benchmark))
                print("Insert testname: success")
                id_testname = curF.lastrowid
                key = str(id_benchmark) + result_entry['name']
                db_testnames[key]=id_testname

            # insert t_testresult
            insert_testresult = (
                "INSERT INTO t_testresult (score, percent, t_testname_id, t_benchresult_id) "
                "VALUES (%s, %s, %s, %s)")
            print("Insert testresult:", result_entry['name'])
            curG.execute(insert_testresult,(float(result_entry['score']), float(result_entry['percent']), id_testname, id_benchresult))
            print("Insert testresult:succeded")
                
        # Commit the changes
        cnx.commit()
    except mysql.connector.Error as e:
        # Rollback in case there is any error
        print('Exception during benchresult storage:', sys.exc_info()[0])
        print("Error code:", e.errno)        # error number
        print("SQLSTATE value:", e.sqlstate) # SQLSTATE value
        print("Error message:", e.msg)       # error message
        print("Error:", e)                   # errno, sqlstate, msg values
        s = str(e)
        print("Error:", s)                   # errno, sqlstate, msg values
        cnx.rollback()
    finally:
        if (cnx.is_connected()):
            cnx.close()

host = 'localhost'
dbname = 'grafdb'
dbuser = 'grafdb'
dbpwd = 'complexPwd'

db_benchmarks = {} # {'title+level': "benchmark_id"}
db_testnames = {}  #  {'benchmark_id+testname': "testname_id"}

def main(argv):
    global host
    global dbname
    global dbuser
    global dbpwd
    path = '.'
    try:
        opts, args = getopt.getopt(argv,"hp:h:d:u:s:",["path=","host=","dbname=","dbuser=","dbpwd="])
    except getopt.GetoptError:
        print('repwriter.py -p <path> -h<host> -d <db> -u <user> -s <pwd>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('repwriter.py -p <path> -h<host> -d <db> -u <user> -s <pwd>')
            sys.exit()
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-d", "--db"):
            dbname = arg
        elif opt in ("-u", "--user"):
            dbuser = arg
        elif opt in ("-s", "--secret"):
            dbpwd = arg
    print('Path is ', path)
    print('Host is ', host)
    print('db is ', dbname)
    print('User is ', dbuser)
    print('pwd is ', dbpwd)

    import_reports(path)

if __name__ == "__main__":
   main(sys.argv[1:])
