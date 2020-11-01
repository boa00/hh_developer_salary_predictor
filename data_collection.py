import requests
import pandas as pd 
from datetime import datetime, date, timedelta

# 20.08.2020 rates  
URL = 'https://api.hh.ru/vacancies/' 
CURRENCIES = {'BYR': 29.61,
       'KGS': 0.95,
       'UZS': 0.0072,
       'UAH': 2.69,
       'EUR': 87.49,
       'USD': 73.83,
       'AZN': 43.43,
       'KZT': 0.18,
       }

def get_vacancies(i, date_from, date_to):
    par = {'per_page': 100, 
           'page': i,
           'text': 'NAME:разработчик',
           'only_with_salary': True,
           'date_from': date_from,
           'date_to': date_to,
           }
    r = requests.get(URL, params=par)
    return r.json()['items']
    
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

def get_description(vacancy_id):
    r = requests.get(URL + vacancy_id)
    return r.json()

# devide into n last days 
# and scrap each day separately
def scrapping_data(date_from, date_to):
    vacancies = list()    
    start_date = datetime(date_from[0], date_from[1], date_from[2])
    end_date = datetime(date_to[0], date_to[1], date_to[2])
    for single_date in daterange(start_date, end_date):
        date_str = single_date.strftime("%Y-%m-%d")
        print(date_str)
        for i in range(1, 15): # ~max 1500 per day 
            # returns [] if the date doesn't match 
            data = get_vacancies(i, date_str, date_str)
            for vacancy in data:
                description = get_description(vacancy['id'])
                snippet = vacancy['snippet']
                description['requirement'] = snippet['requirement'] if snippet.get('requirement') is not None else ''
                description['responsibility'] = snippet['responsibility'] if snippet.get('responsibility') is not None else ''
                vacancies.append(description)
    return vacancies
  

data = scrapping_data((2020, 10, 1), (2020, 10, 1))

# removing dublicates by ID and converting into the DataFrame 
data = sorted(data, key=lambda k: k['id']) 
data = [data[i] for i in range(len(data)) if i == 0 or data[i]['id'] != data[i-1]['id']]
df = pd.DataFrame(data)
    
# deciding which columns to include for data manipulation 
columns_left = ['name', 'responsibility',
                'area', 'salary', 'requirement',
                'experience', 'schedule', 
                'description', 'employment',
                    ]
df.drop(df.columns.difference(columns_left), 1, inplace=True)

# changing currencies and ranges for salaries
def currency_change(v):
    s_from = v['from']
    s_to = v['to']
    s_curr = v['currency']
    gross = v['gross']
    if s_from is None:
        s_from = s_to / 1.5
    if s_to is None:
        s_to = s_from * 1.5
    if s_curr != 'RUR':
        s_from = s_from * CURRENCIES[s_curr]
        s_to = s_to * CURRENCIES[s_curr]
    if not gross:
        s_from = s_from / 0.87
        s_to = s_to / 0.87
    return (s_to + s_from) // 2

df['salary'] = df['salary'].apply(currency_change)

# deleting salaray outliers based on IQR
Q1 = df['salary'].quantile(0.25)
Q3 = df['salary'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df.salary < Q3 + 1.5 * IQR) & (df.salary > Q1 - 1.5 * IQR)]

# data transformation for categorical columns
df['area'] = df['area'].apply(lambda x: x['name'] if x['id'] == '1' or x['id'] == '2' else 'Не МСК/С-П')
df['experience'] = df['experience'].apply(lambda x: x['id'])
df['schedule'] = df['schedule'].apply(lambda x: x['id'])
df['employment'] = df['employment'].apply(lambda x: x['id'])
df = pd.get_dummies(df, columns=['area', 'experience', 'schedule', 'employment'])

# create dummy variables for skills

# parse important skills from .txt
key_skills = []
with open("skills.txt", "r") as technologies:
    for skills in technologies:
        skills = skills[:-1].split(',')
        key_skills.append(skills)

# get dummies
def count_skills(row, skills):
    if any(skill in row['description'].lower() or skill in row['requirement'].lower()
           or skill in row['responsibility'].lower() or skill in row['name'].lower() 
           for skill in skills):
        return 1
    else:
        return 0
    
for key_skill in key_skills:
    df[key_skill[0]] = df.apply(count_skills, skills=key_skill, axis=1)

# adding senior/junior/team lead distinction
senior = ['senior', 'сеньор', 'ведущий', 'старшый']
junior = ['junior', 'джуниор', 'младший', 'начинающий']

df['senior'] = df['name'].apply(lambda x: 1 if any(name in x for name in senior) else 0) 
df['junior'] = df['name'].apply(lambda x: 1 if any(name in x for name in junior) else 0) 

# drop inofrmation and name columns as they are useless now 
df.drop(['description', 'requirement', 'responsibility', 'name'], axis=1, inplace=True)

# export to scv
df.to_csv('data.csv', index=False)
