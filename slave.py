from radon.metrics import mi_visit
from radon.complexity import cc_visit, cc_rank
from pygit2 import Repository, clone_repository
import requests, json
from time import time
import sys




# computes the complexity of all .py files in the given list
def compute_complexity(source):
    result =[]
    blocks = cc_visit(source)
    for func in blocks:
        result.append(func.name+"- CC Rank:"+cc_rank(func.complexity))
    return result

# walks through the tree of the given repo and stores any .py files in a list
def get_data(tree, repo):
    sources = []
    for entry in tree:
        if ".py" in entry.name:
            sources.append(entry)
        if "." not in entry.name:
           if entry.type == 'tree':
                new_tree = repo.get(entry.id)
                sources += (get_data(new_tree, repo))
    return sources

# decodes the files stored in the list
def extract_files(sources):
    files = []
    for source in sources:
        files.append(repo[source.id].data.decode("utf-8"))
    return files


# ask for work from the given iurl
def get_work(repo):
    post = requests.post('http://127.0.0.1:5000/executiontime', json={'start_time': time()})
    response = requests.get('http://127.0.0.1:5000/work', params={'key': 'value'})
    while response.status_code == 200:
        response.encoding = 'utf-8'
        json_file = response.json()
        post.encoding = 'utf-8'
        post_file = post.json()
        executiontime = post_file['executiontime']
        id = json_file['id']
        tree = repo.get(json_file['commit']).tree
        sources = get_data(tree, repo)
        files = extract_files(sources)
        return files, id, executiontime


# post results to the url
def send_results(result):
    requests.post('http://127.0.0.1:5000/results', json=result,  params={'key': 'value'})
    response = requests.get('http://127.0.0.1:5000/results',  params={'key': 'value'})
    return response

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ("Correct usage: script, localfilepath, gitrepopath")
        exit()
   
    local_file_path = str(sys.argv[1])
    git_File_name = str(sys.argv[2])
    bool = True
    executiontime_list = []
    result_list = []
    id = 0
    while bool: #run until work is finished
        try:
            repo = Repository(local_file_path)
        except:
            #repo_url = 'https://github.com/rubik/radon.git'
            #repo_path = 'D:/Users/AJ/PycharmProjects/untitled1/radon'
            repo = clone_repository(git_File_name, local_file_path)
        commits = []
        for commit in repo.walk(repo.head.target):
            commits.append(repo.get(commit.id))
        try:
            work, id, executiontime = get_work(repo)
            print(id)
            executiontime_list.append(executiontime)
        except:
            bool = False
            print("Process Terminated")
    report = { 'executiontime': executiontime_list}
    send_results(report)