import requests
from bs4 import BeautifulSoup
from cs50 import SQL

DATAADRESSES = {
    "acceptanceRate" : "[2] /// Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO",
    "SFRatio" : "[5] /// Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO",
    "name" : "[0] /// Heading__HeadingStyled-sc-1w5xk2o-0 kjsWoc Heading-sc-1w5xk2o-1 Wakanda__Title-rzha8s-10 kQuiLM ZGtHl",
    "startingSalary" : "[0] /// Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO",
    "gradRate" : "[6] /// Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO",
    "NCAA division" : "[7] /// Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO",
    "Cars on campus" : "[8] /// Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO",
    "healthInsurance" : "[9] /// Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO",
    "rank" : "",
    "majors" : "see function",
    "genderBreakdown" : "see function",
    "classBreakdown" : "see function"
    }

# find nth occurance of char in a string
def findNth(string, char, n):
    breaker = string.find(char)
    while breaker >=0 and n > 1:
        breaker = string.find(char, breaker + len(char))
        n -= 1
    return breaker

# gets the additional URL information for each college
def getAddress(data):
    tmp = str(data)
    start = tmp.find("href")
    end = tmp.find("\"", start + 7)
    return tmp[start + 6:end]

# get the formatted information given the class
def getFormattedInfo(url, headers, className):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    return soup.find_all(class_=className)

# get the top 3 majors of a school as a string given the school url
def getMajors(url, headers):
    data = getFormattedInfo(url, headers, "Raw-slyvem-0 util__RawContent-sc-1kd04gx-2 dNiWsv jhKFqT")[3].text
    data = data[data.find("include:") + 9:]
    if findNth(data, ";", 3) == -1:
        return data[:findNth(data, ".", 1)]
    return data[:findNth(data, ";", 3)]

# get the class-size breakdown given the school url (as an array [<20, 20-49. 50+])
def getClassBreakdown(url, headers):
    breakdown = []
    if not getFormattedInfo(url, headers, "BarChartStacked__Legend-wgxhoq-4 dupHBn"):
        return ["N/A", "N/A", "N/A"]
    data = getFormattedInfo(url, headers, "BarChartStacked__Legend-wgxhoq-4 dupHBn")[0].text
    # find < 20
    data = data[data.find("students") + 8:]
    breakdown.append(data[:findNth(data, "%", 1) + 1])

    # find 20-49
    data = data[findNth(data, "%", 1) + 6:]
    breakdown.append(data[:findNth(data, "%", 1) + 1])

    # find 50+
    data = data[data.find("more") + 4:]
    breakdown.append(data) 

    return breakdown

# get genderbreakdown of a school (as an array [male %, female %])
def getGenderBreakdown(url, headers):
    breakdown = []
    try:
        data = getFormattedInfo(url, headers, "BarChartStacked__Legend-wgxhoq-4 dupHBn")[1].text
    except:
        try: 
            data = getFormattedInfo(url, headers, "BarChartStacked__Legend-wgxhoq-4 dupHBn")[0].text
        except:
            return ["N/A", "N/A"]

    # get male data
    data = data[4:]
    breakdown.append(data[:findNth(data, "%", 1) + 1])

    # get female data
    data = data[findNth(data, "%", 1) + 7:]
    breakdown.append(data)

    return breakdown

# get rank of a school given the url
def getCollegeRank(url, headers):
    data = getFormattedInfo(url, headers, "Paragraph-sc-1iyax29-0 ProfileHeading__RankingParagraph-sc-1n3m2r3-4 eMgXHu fTtVpn")[0].text
    data = data[1:findNth(data, " ", 1)]
    return data

def getSFRatio(url, headers):
    data = getFormattedInfo(url, headers, "Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO")[5].text
    data = data[:findNth(data, ":", 1)]
    return data

# add all information about a college given the college url
def addCollegeInfo(url, headers, database):
    
    # get acceptanceRate
    aR = getFormattedInfo(url, headers, "Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO")[2].text

    # get sfRatio
    sfRatio = getSFRatio(url, headers)

    # get name
    name = getFormattedInfo(url, headers, "Heading__HeadingStyled-sc-1w5xk2o-0 kjsWoc Heading-sc-1w5xk2o-1 Wakanda__Title-rzha8s-10 kQuiLM ZGtHl")[0].text

    # get rank
    rank = getCollegeRank(url, headers)

    # get starting sal
    startingSal = getFormattedInfo(url, headers, "Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO")[0].text

    # get gradRate
    gradRate = getFormattedInfo(url, headers, "Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO")[6].text

    # get NCAA
    ncaa = getFormattedInfo(url, headers, "Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO")[7].text

    # get carRate
    carRate = getFormattedInfo(url, headers, "Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO")[8].text

    # get healthInsurance
    healthInsurance = getFormattedInfo(url, headers, "Paragraph-sc-1iyax29-0 Section__DataCell-ply21t-2 hJyuQa hTDNHO")[9].text

    # get majors
    majors = getMajors(url, headers)

    # get maleRate and femaleRate
    genderBreakdown = getGenderBreakdown(url, headers)
    maleRate = genderBreakdown[0]
    femaleRate = genderBreakdown[1]

    # get smallClass, medClass, and largeClass
    classBreakdown = getClassBreakdown(url, headers)
    smallClass = classBreakdown[0]
    medClass = classBreakdown[1]
    largeClass = classBreakdown[2]

    # add to database
    database.execute("INSERT INTO colleges (acceptanceRate, sfRatio, name, rank, startingSalary, gradRate, NCAA, carRate, healthInsurance, majors, maleRate, femaleRate, smallClass, medClass, largeClass) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", aR, sfRatio, name, rank, startingSal, gradRate, ncaa, carRate, healthInsurance, majors, maleRate, femaleRate, smallClass, medClass, largeClass)

def main():
    # load database
    if SQL("sqlite:///collegesFull.db"):
        db = SQL("sqlite:///collegesFull.db")
    else:
        return 1
    
    # loading variables for ULRs and headers
    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    baseURL = "https://usnews.com"
    URL = "https://usnews.com/best-colleges/rankings/national-universities?_page="

    # go through pages of colleges
    for i in range(50):
        # get the requests for the page
        results = getFormattedInfo(URL + str(i+1), headers, "Anchor-byh49a-0 DetailCardColleges__StyledAnchor-cecerc-7 kQpddJ eKrerU card-name")
        for result in results:
            additionalInfo = getAddress(result)
            addCollegeInfo(baseURL + str(additionalInfo), headers, db)
        print("Finished page " + str(i))
    
    print("Complete!")



if __name__ == "__main__":
    main()