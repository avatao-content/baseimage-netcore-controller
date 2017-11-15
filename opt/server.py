from flask import Flask, jsonify, request, abort, make_response
from subprocess import STDOUT, check_output
from shutil import copyfile
import subprocess
import os
import cgi
import sys
import json
import re

def getfails(output):
# Returns empty list on success
	try:
		failed = []
		output = output.splitlines()
		for line in output:
			if "{" in line:
				line = line[line.index('{'):]
				item = json.loads(line)
				if item["message"] == "testFailed":
					# Upper split
					words = filter(None, re.split("([A-Z][^A-Z]*)", item["testName"].split(".")[-1]))
					# Formatting
					failed.append(' '.join(words).lower().capitalize())
		return failed
	except Exception as e:
		if not os.environ['SECRET'] == "secret":
			return ["Parsing error! (Please contact support@avatao.com)"]
		return ["Parsing error: " + str(e) + " (Please contact support@avatao.com)"]

os.chdir('/home/controller/Program/Test')

app = Flask(__name__)

@app.route('/%s/test' % os.environ['SECRET'], methods=['GET'])
def test():   
    BUILD = ['dotnet', 'build', '--no-restore', '/home/controller/Program/Program.sln']
    TEST = ['dotnet', 'xunit', '-nobuild', '-xml', 'test_results.xml']
    try:
        # Copying solution
        copyfile('/opt/Solution.cs', '/home/controller/Program/App/Program.cs')
        # Building project
        output = subprocess.check_output(BUILD, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as exc:
        # Parsing build errors
        output = exc.output.decode('utf-8')
        # Returning them in 'pre' and 'code' blocks (to keep format)
        error = '<pre><code>' + cgi.escape(output) + '</code></pre>'
        return jsonify(solved=False, message=error)
    try:
        # Running unit tests
        subprocess.call(TEST)
        error = ""
        
        # Parsing output
        with open('/home/controller/Program/Test/test_results.xml') as f:
            ts, tr = xunitparser.parse(f)

        for tc in ts:
            print('Class %s, method %s' % (tc.classname, tc.methodname))
            if not tc.good:
                error += str(tc.methodname) + "\n"
        # Solution is accepted if no errors found
        if not error:
            return make_response('OK', 200)
        else:
            abort(500, error)                 
    except Exception as e:
        abort(500, e)


@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    BUILD = ['dotnet', 'build', '--no-restore', '/home/controller/Program/Program.sln']
    TEST = ['dotnet', 'xunit', '-nobuild', '-json']
    try:
        # Copying solution
        copyfile('/home/user/solvable/Program.cs', '/home/controller/Program/App/Program.cs')
        # Building project
        output = subprocess.check_output(BUILD, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as exc:
        # Parsing build errors
        output = exc.output.decode('utf-8')
        # Returning them in 'pre' and 'code' blocks (to keep format)
        error = '<pre><code>' + cgi.escape(output) + '</code></pre>'
        return jsonify(solved=False, message=error)
    try:
        subprocess.check_output(TEST, stderr=subprocess.STDOUT)
        return jsonify(solved=True)
                  
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode('utf-8')
        result = "TEST FAILED\n"
        for t in getfails(output):
            result+= t + "\n"
        return jsonify(solved=False, message=result.rstrip())
    except Exception as e:
        return jsonify(solved=False, message=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ['CONTROLLER_PORT']),
            debug=True)
