import requests as req
from bs4 import BeautifulSoup as soup
import csv
import pandas as pd

myFieldNames = ['JobTitle', 'Company', 'Location', 'ApplicationLink']
outfile = open('jobResults.csv', 'w', newline='')
myWriter = csv.DictWriter(outfile, delimiter=',', fieldnames=myFieldNames)
myWriter.writeheader()


# this function performs makes a request for a query on a website via a URL
# the name of the website to be queried can be passed in as a string
# a csv will be written for the values Job title, company, location and
# link to apply
def querySite(websiteStr):
    # url and search keys for monster.com
    if websiteStr == 'monster':
        # I have page count set to 3 (about 75 results) if a query does
        # not have this many results no errors happen. So this hard code is
        # OK. If this was an issue you'd want to get the number of results
        # first and then make the page count dependent on that.
        url = 'https://www.monster.com/jobs/search/?q=' + jobTitle + \
              '&where=' + location + "&stpage=1&page=3"
        # these keys are intended to be chaged for other websites dependent on
        # html structure
        allResultsKey = 'ResultsContainer'
        jobElementsKey = 'card-content'
        # number of hrefs before job links start
        offSet = 22
        jobElemsLoc = 'section'
        jobTitleLoc = 'title'
        companyLoc = 'company'
        locationLoc = 'location'  # haha

    # url and search keys for ZipRecruiter.com
    if websiteStr == 'ZipRecruiter':
        url = 'https://www.ziprecruiter.com/candidate/search?search='+jobTitle + '&location=' +location
        allResultsKey = 'job_results'
        jobElementsKey = 'job_result   t_job_result'
        jobElemsLoc = 'article'
        jobTitleLoc = 'just_job_title'
        companyLoc = 'job_org'
        locationLoc = 't_location_link location'
        offSet = 22

    # to expand add conditionals for other job searching sites
    # IE Glassdoor, Google, Indeed
    # some companies make this a lot harder than others through encrypted links
    # and urls. Monster is really easy in terms of their layout structure.

    myPage = req.get(url)
    mySoup = soup(myPage.content, 'html.parser')

    # this loop gets all the links from href types. I would have liked to have
    # done this inside the job_elems loop that would negete the need for offSet
    links_with_text = []
    for a in mySoup.find_all('a', href=True):
        if a.text:
            links_with_text.append(a['href'])

    allResults = mySoup.find(id=allResultsKey)
    job_elems = allResults.find_all(jobElemsLoc, class_=jobElementsKey)

    count = offSet
    for job_elem in job_elems:
        title_elem = job_elem.find('h2', class_=jobTitleLoc)
        company_elem = job_elem.find('div', class_=companyLoc)
        location_elem = job_elem.find('div', class_=locationLoc)

        if None in (title_elem, company_elem, location_elem):
            continue
        # prints just for quick checking
        # text.strip removes all white space chars including \n and similar
        print(title_elem.text.strip())
        print(company_elem.text.strip())
        print(location_elem.text.strip())
        print(links_with_text[count])
        print()
        # too lazy to store the above in vars so I rewrote the strips
        myWriter.writerow({'JobTitle': title_elem.text.strip(),
                           'Company': company_elem.text.strip(),
                           'Location': location_elem.text.strip(),
                           'ApplicationLink': links_with_text[count]})
        # need this count to get our current link to match with job element
        count += 1


# request query for site monster.com
jobTitle = 'process-engineer'
location = 'seattle'
querySite('monster')
# Well zip recruiter hits me with a captcha; code is good though
# querySite('ZipRecruiter')
outfile.close()

# Lets process the data now
# I want to count the number of times process and engineer apear in the
# same string for job title. This will allow us to analyze how well the
# job search engines perform based on my requested search
df = pd.read_csv("jobResults.csv", names=myFieldNames)
jobTitles = df.JobTitle.to_list()
subStr = 'Process'
processJobs = [string for string in jobTitles if subStr in string]
# print(processJobs)
subStr = 'Engineer'
engineerJobs = [string for string in jobTitles if subStr in string]
# print(engineerJobs)
subStr = 'Process Engineer'
processEngineerJobs = [string for string in jobTitles if subStr in string]
# print(processEngineerJobs)
df.close()
# now analysis on these lists
totalJobs = len(jobTitles) - 1  # use -1 bc of header
numProcessJobs = len(processJobs)
numEngineerJobs = len(engineerJobs)
numProcessEngineerJobs = len(processEngineerJobs)
# but we have overlap here bc process engineer jobs get counted twice
numProcessJobs -= numProcessEngineerJobs
numEngineerJobs -= numProcessEngineerJobs
# find percentages that will tell us the patterns of search results
percentProcessJobs = numProcessJobs / totalJobs
percentEngineerJobs = numEngineerJobs / totalJobs
percentProcessEngineerJobs = numProcessEngineerJobs / totalJobs
print("Total number of Jobs found: " + str(totalJobs))
print("Process only Jobs: " + str(numProcessJobs) + ", " +str(round(percentProcessJobs, 4)*100) + "%")
print("Engineering only Jobs: " + str(numEngineerJobs) + ", " +str(round(percentEngineerJobs, 4)*100) + "%")
print("Process Engineer Jobs: " + str(numProcessEngineerJobs) + ", " +str(round(percentProcessEngineerJobs, 4)*100) + "%")