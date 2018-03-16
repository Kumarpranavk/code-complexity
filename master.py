from flask import Flask, request, jsonify
from time import time
from pygit2 import Repository, clone_repository
import sys


app = Flask(__name__)

# give work to any worker who access the url
@app.route('/work', methods=['GET'])
def give_work():
    try:
        repo = Repository(local_file_path)
    except:
        #repo_url = git_File_name
        #repo_path = local_file_path
        repo = clone_repository(git_File_name, local_file_path)
    commits = []
    for commit in repo.walk(repo.head.target):
        commits.append(repo.get(commit.id))
    global next_task
    if next_task < len(commits):
        commit_hash = commits[next_task]
        next_task += 1
        return jsonify({'commit': str(commit_hash.id), 'id': next_task})
    else:
        return "No Work"

# send Execution time
@app.route('/executiontime' , methods=['POST'])
def execution_time():
    start_time = request.json
    end_time = time() - int(start_time['start_time'])
    return jsonify({'executiontime': end_time})

# store results that are sent to this url
@app.route('/results', methods=['POST','GET'])
def store_result():
    global executiontime_list, execution_time, result
    executiontime_list = []
    if request.method == 'POST':
        result = request.json
        executiontime_list = result['executiontime']
        execution_time = sum(executiontime_list)
        return jsonify({ 'execution_time': execution_time})
    else:
        return jsonify({ 'execution_time': execution_time})

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ("Correct usage: script, localfilepath, gitrepopath")
        exit()
    
    local_file_path = str(sys.argv[1])
    git_File_name = str(sys.argv[2])
    next_task = 0
    global result_list
    result_list = []
app.run(threaded=True, debug=True)
