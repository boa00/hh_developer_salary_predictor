import requests
import pandas as pd

class Vacancy:

    URL = 'https://api.hh.ru/vacancies/'
    columns = list(pd.read_csv('/home/boa00/bot/data.csv').columns)[1:]

    def __init__(self, vacancy_id):
        self.vacancy = requests.get(self.URL+vacancy_id).json()
        self.vacancy_df = pd.DataFrame(columns=self.columns)

    def transform(self):
        # if the id is wrong return None
        if self.vacancy['description'] == 'Not Found':
            return
        self.vacancy_df.loc[0] = [0]*100 # creating a single row for the request
        # creating all the dummies for the model
        self._area_dummies()
        self._experience_dummies()
        self._schedule_dummies()
        self._schedule_dummies()
        self._employment_dummies()
        self._skills_dummies()
        self._title_dummies()
        return self.vacancy_df

    def _area_dummies(self):
        self.vacancy_df['area_Москва'][0] = 1 if self.vacancy['area']['id'] == '1' else 0
        self.vacancy_df['area_Не МСК/С-П'][0] = 1 if int(self.vacancy['area']['id']) > 2 else 0
        self.vacancy_df['area_Санкт-Петербург'][0] = 1 if self.vacancy['area']['id'] == '2' else 0

    def _experience_dummies(self):
        self.vacancy_df['experience_between1And3'][0] = 1 if self.vacancy['experience']['id'] == 'between1And3' else 0
        self.vacancy_df['experience_between3And6'][0] = 1 if self.vacancy['experience']['id'] == 'between3And6' else 0
        self.vacancy_df['experience_moreThan6'][0] = 1 if self.vacancy['experience']['id'] == 'moreThan6' else 0
        self.vacancy_df['experience_noExperience'][0] = 1 if self.vacancy['experience']['id'] == 'noExperience' else 0

    def _schedule_dummies(self):
        self.vacancy_df['schedule_flexible'][0] = 1 if self.vacancy['schedule']['id'] == 'flexible' else 0
        self.vacancy_df['schedule_flyInFlyOut'][0] = 1 if self.vacancy['schedule']['id'] == 'flyInFlyOut' else 0
        self.vacancy_df['schedule_fullDay'][0] = 1 if self.vacancy['schedule']['id'] == 'fullDay' else 0
        self.vacancy_df['schedule_remote'][0] = 1 if self.vacancy['schedule']['id'] == 'remote' else 0
        self.vacancy_df['schedule_shift'][0] = 1 if self.vacancy['schedule']['id'] == 'shift' else 0

    def _employment_dummies(self):
        self.vacancy_df['employment_full'][0] = 1 if self.vacancy['employment']['id'] == 'full' else 0
        self.vacancy_df['employment_part'][0] = 1 if self.vacancy['employment']['id'] == 'part' else 0
        self.vacancy_df['employment_probation'][0] = 1 if self.vacancy['employment']['id'] == 'probation' else 0
        self.vacancy_df['employment_project'][0] = 1 if self.vacancy['employment']['id'] == 'project' else 0

    def _skills_dummies(self):
        # first, converting key_skills to string for easier search
        self.vacancy['key_skills'] = ' '.join([k['name'] for k in self.vacancy['key_skills']])
        key_skills = self._load_skills()
        for skills in key_skills:
            if any(skill in self.vacancy['name'].lower() or skill in self.vacancy['description'].lower()
                   or skill in self.vacancy['key_skills'].lower() for skill in skills):
                    self.vacancy_df[skills[0]][0] = 1

    def _title_dummies(self):
        senior = ['senior', 'сеньор', 'ведущий', 'старшый']
        junior = ['junior', 'джуниор', 'младший', 'начинающий']

        self.vacancy_df['senior'] = 1 if any(title in self.vacancy['name'] for title in senior) else 0
        self.vacancy_df['junior'] = 1 if any(title in self.vacancy['name'] for title in junior) else 0

    def _load_skills(self):
        key_skills = []
        # problem in opening file here
        with open('/home/boa00/bot/skills.txt', "r") as technologies:
            for skills in technologies:
                skills = skills[:-1].split(',')
                key_skills.append(skills)
        return key_skills








