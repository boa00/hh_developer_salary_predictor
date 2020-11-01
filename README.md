
# Прогнозирование зарплаты разрабочика с HH.ru 

<p align="center"><img src="https://i.ibb.co/jh6Vvhr/photo-2020-09-05-10-30-25.jpg" width="320" height="320"></p>

Больше чем у трети всех вакансий программиста на HH.ru не указана зарплата. Целью было создать приложение, которое, основываясь на описании вакансии (требования, локация, опыт работы и т.д.), может более-менее точно предсказывать диапазон ожидаемой зарплаты.

# Summary проекта: 

* Предсказывет зарплату с RMSE ~ 39к рублей
* Обучение проводилось на 6к вакансий (с указанными зарплатами) взятых с официального hh.ru API (данные от 23.07.2020 до 23.08.2020)
* Использованные модели: Lasso и Ridge regressions, Random Forest Regression, Support Vector Rregression и Gradient Boosting Regression
* Есть Telegram Бот как front-end для проекта, через него можно получать прогноз по зарплате на основе URL вакансии с HH.ru, название: @HHPredictorBot

# Сбор данных 

Все данные для обучения были взяты с официального API от HH.ru по поисковому запросу "разработчик". 
Единственная проблема была в том, что у HH.ru есть ограничение только на 2к запросов "за раз". Чтобы обойти это, я парсил данные по дате. Иными словами, я ставил начальную и конечную дату, и потом парсил каждый день отдельно. Так как за каждый отдельный день никогда не набиралось больше 1.5к вакансий, то это сработало. 

# Использованные переменные

* Местоположение. Чтобы уменьшть кол-во переменных, оставил только три категории: Москва/Санкт-Питербург/Не МСК или Сб
* Опыт работы 
* Тип занятости 
* Полный/неполный день
* Требования. У каждой вакансии была колонка "key skills", где работадатель указывал 3-5 самых важным навыка. Я запарсил со всех вакансий это все в один set, и уже оттуда выбрал самые популярные и добавил их в один skills.txt файл, из которых потом сделал dummy variables
* Позиция: senior/junior

# Обработка данных

* Для зарплат, где был указан диапазон, приравнял значение к среднему
* У многих вакансий указана зарплата только "от" или только "до". В среднем, одно больше/меньше второго в 1.5 раза, так что умножил/поделил на 1.5, чтобы получить полный диапазон
* Приравнял все запралыт к одной валюте и конвертировал в "gross" (т.е. до налогов)
* Очистил от outlires по зарплате 
* Добавил dummy varialbes для всех навыков, т.е. 1 если указан указан "python" в описании вакансии и 0 в противном случае
* Добавил categorical varialbes для остальных параметров (см. "Использованные переменные" выше)

<p align="center"><img src="https://i.ibb.co/vsZSQKn/Figure-2020-10-03-211811.png" width="372" height="273"></p>

# Результаты моделей 

Я разбил train/test на 80/20 и использовал GridSearchCV для подбора параметров. Для критерия выбарл RMSE как наиболее интуитивную оценку ошибки (в тыс. рублей). Результаты:

* Lasso. Train: 42196.17322391547; Predict: 44037.191044383784
* Ridge. Train: 41888.222214730384; Predict: 43655.01887960997
* Random Forest. Train: 39698.44912143441; Predict: 40279.525241149306
* Support Vector Regression. Train: 40064.76307332772; Predict: 40567.24243264028
* Gradient Boosting. Train: 39519.08097052617; Predict: 39980.868239610376 (winner)

Lasso и Ridge были выбраны, потому что у нас большое кол-во переменных (около 100), так что какая-та форма регуляризация необходима. Random Forest и Gradient Boosting должны неплохо работать на этих данных, т.к. все параметры categorical. Support Vector Regression просто в целом хороший алгоритм.

# Продакшн

Для работы с программой я создал Telegram Бота. Для взаимодейсвтием с Telegram API я использовал WebHook (через Flask) и загрузил все это на бесплатный хостинг PythonAnywhere. Бот работает круглосуточно: @HHPredictorBot

<p align="center"><img src="https://i.ibb.co/0Bh0wqw/Untitled.png"</p>
  
# References

* Официальное API от HH.ru: https://github.com/hhru/api
* Плейлист на YouTube который сильно помог с WebHook частью: https://www.youtube.com/playlist?list=PLlWXhlUMyooaTZA4vxU9ZRZQPCFxUq9VA
* Хорошо расписаны основы для Телеграм Бота: https://github.com/SouravJohar/gangsta
