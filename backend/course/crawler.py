import requests
from bs4 import BeautifulSoup as bs
import xlrd


class Crawler:
    search_url = 'http://sugang.snu.ac.kr/sugang/cc/cc100.action'
    excel_url = 'http://sugang.snu.ac.kr/sugang/cc/cc100excel.action'
    semester_name = {
        'U000200001U000300001': '1',
        'U000200001U000300002': 'S',
        'U000200002U000300001': '2',
        'U000200002U000300002': 'W'
    }
    # srchOpenSchyy : year
    # srchOpenShtm : semester
    # srchOpenUpSbjtFldCd : area
    # srchOpenSbjtFldCd : subarea
    form_data = {
        'srchOpenUpSbjtFldCd': '',
        'srchOpenSbjtFldCd': '',
        'srchOpenShtm': '',
        'srchCond':'1',
        'srchOpenSchyy': '',
        'srchCptnCorsFg':'',
        'srchOpenShyr':'',
        'srchSbjtCd':'',
        'srchSbjtNm':'',
        'srchOpenUpDeptCd':'',
        'srchOpenDeptCd':'',
        'srchOpenMjCd':'',
        'srchOpenSubmattCorsFg':'',
        'srchOpenSubmattFgCd':'',
        'srchOpenPntMin':'',
        'srchOpenPntMax':'',
        'srchCamp':'',
        'srchBdNo':'',
        'srchProfNm':'',
        'srchTlsnAplyCapaCntMin':'',
        'srchTlsnAplyCapaCntMax':'',
        'srchTlsnRcntMin':'',
        'srchTlsnRcntMax':'',
        'srchOpenSbjtTmNm':'',
        'srchOpenSbjtTm':'',
        'srchOpenSbjtTmVal':'',
        'srchLsnProgType':'',
        'srchMrksGvMthd':'',
        'srchFlag':'',
    }
    def get_areas(self, year, semester):
        form_data = self.form_data.copy()
        form_data['srchOpenSchyy'] = str(year)
        form_data['srchOpenShtm'] = semester
        search_page = requests.post(self.search_url, data=form_data)
        soup = bs(search_page.text, 'html5lib')
        select = soup.find('select',{'name':'srchOpenUpSbjtFldCd'})
        options = select.find_all('option')
        areas = list(map(lambda op : {
            'code': op['value'],
            'name': op.text.strip()
            }, options))
        return list(filter(lambda s: s['code']!='', areas))

    def get_subareas(self, year, semester, area):
        form_data = self.form_data.copy()
        form_data['srchOpenSchyy'] = str(year)
        form_data['srchOpenShtm'] = semester
        form_data['srchOpenUpSbjtFldCd'] = area['code']
        search_page = requests.post(self.search_url, data=form_data)
        soup = bs(search_page.text, 'html5lib')
        select = soup.find('select',{'name':'srchOpenSbjtFldCd'})
        options = select.find_all('option')
        subareas = list(map(lambda op: {
            'code': op['value'],
            'name': op.text.strip()
            }, options))
        return list(filter(lambda s: s['code']!='', subareas))

    def get_courses(self, year, semester, area, subarea):
        form_data = self.form_data.copy()
        form_data['srchOpenSchyy'] = str(year),
        form_data['srchOpenShtm'] = semester,
        form_data['srchOpenUpSbjtFldCd'] = area['code'],
        form_data['srchOpenSbjtFldCd'] = subarea['code'],
        excel = requests.post(self.excel_url, form_data)
        try:
            workbook = xlrd.open_workbook(file_contents=excel.content)
        except Exception as e:
            print(e)
            return []
        sheet = workbook.sheet_by_index(0)
        res = []
        for row in range(3, sheet.nrows):
            course = {
                    'year': year,
                    'semester': self.semester_name[semester],
                    'code': sheet.cell_value(row, 5),
                    'number': sheet.cell_value(row, 6),
                    'title': sheet.cell_value(row, 7),
                    'credit': sheet.cell_value(row, 9),
                    'category': sheet.cell_value(row, 0),
                    'language': sheet.cell_value(row, 19),
                    'area': area['name'],
                    'subarea': subarea['name'],
                    'collage': sheet.cell_value(row, 1),
                    'dept': sheet.cell_value(row, 2)
                    }
            res.append(course)
        return res

    def crawl_courses(self, start, end=None):
        if end is None:
            end = start + 1
        courses = []
        for year in range(start, end):
            for semester in list(self.semester_name.keys()):
                areas = self.get_areas(year, semester)
                for area in areas:
                    subareas = self.get_subareas(year, semester, area)
                    for subarea in subareas:
                        cs = self.get_courses(year, semester, area, subarea)
                        courses.extend(cs)
        return courses
