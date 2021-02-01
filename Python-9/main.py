import requests
import csv
from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
"""
These are the URLs that will give you remote jobs for the word 'python'

https://stackoverflow.com/jobs?r=true&q=python
https://weworkremotely.com/remote-jobs/search?term=python
https://remoteok.io/remote-dev+python-jobs

Good luck!
"""
app = Flask("LastChallenge")

db = []


def get_wework(programming, job):
    wework_url = f"https://weworkremotely.com/remote-jobs/search?utf8=%E2%9C%93&term={programming}"
    wework_soup = BeautifulSoup(requests.get(wework_url).text, "html.parser")
    wework_job_list = wework_soup.find("section", {"id": "category-2"})
    wework_ul = wework_job_list.find("ul")
    wework_li = wework_ul.find_all("li")

    for we in wework_li:
        if we.find("span", {"class": "company"}) is None:
            pass
        else:
            obj = {
                "company": we.find("span", {"class": "company"}).text,
                "title": we.find("span", {"class": "title"}).text,
                "href": f"https://weworkremotely.com{we.find('a')['href']}"
            }
        job.append(obj)


def get_remoteok(programming, job):
    remoteok_url = f"https://remoteok.io/remote-{programming}-jobs"
    remoteok_soup = BeautifulSoup(
        requests.get(remoteok_url).text, "html.parser")
    remoteok_table = remoteok_soup.find("table")
    remoteok_tr = remoteok_table.find_all("tr", {"class": "job"})

    for re in remoteok_tr:
        obj = {
            "company": re.find("h3", {"itemprop": "name"}).text,
            "title": re.find("h2", {"itemprop": "title"}).text,
            "href": f"https://remoteok.io/{re.find('a', {'class': 'preventLink'})['href']}"
        }
        job.append(obj)


def get_stackOF(programming, job):
    stackOF_url = f"https://stackoverflow.com/jobs?q={programming}"
    stackOF_soup = BeautifulSoup(requests.get(stackOF_url).text, "html.parser")
    stackOF_div = stackOF_soup.find("div", {"class": "previewable-results"})
    stackOF_select = stackOF_div.find_all("div", {"class": "-job"})

    for st in stackOF_select:
        origin_company = str(st.find("h3", {"class": "mb4"}).find("span"))
        f_replace = origin_company.replace("<span>", "")
        s_replace = f_replace.replace("</span>", "")
        t_replace = s_replace.replace("\r\n", "")
        result_replace = t_replace.rstrip()

        obj = {
            "company": result_replace,
            "title": st.find("a", {"class": "stretched-link"}).text,
            "href": f"https://stackoverflow.com{st.find('a', {'class': 'stretched-link'})['href']}"
        }
        job.append(obj)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/find")
def find_all_jobs():
    job_list = []
    programming = request.args.get("programming").lower()
    if programming in db:
        index = db.index(programming)
        job_list = db[index+1]
    else:
        db.append(programming)
        get_remoteok(programming, job_list)
        get_stackOF(programming, job_list)
        get_wework(programming, job_list)
        db.append(job_list)
    return render_template("find.html", len_jobs=len(job_list), title=programming, jobs=job_list)


@app.route("/download")
def download():
    job_list = []
    job = request.args.get("job").lower()
    index = db.index(job)
    job_list = db[index+1]
    file = open("jobs.csv", mode="w", encoding="utf-8")
    writer = csv.writer(file)
    writer.writerow(['company', 'title', 'href'])
    for jobs in job_list:
        writer.writerow(list(jobs.values()))
    return send_file(
        "jobs.csv", mimetype="text/csv",
        attachment_filename=f'{job}.csv',
        as_attachment=True
    )


@app.after_request
def add_header(rqst):
    rqst.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    rqst.headers["Pragma"] = "no-cache"
    rqst.headers["Expires"] = "0"
    rqst.headers['Cache-Control'] = 'public, max-age=0'
    return rqst


app.run(host="0.0.0.0")
