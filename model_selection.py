import pandas as pd
import joblib
from math import sqrt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR


df = pd.read_csv('data.csv')

y = df['salary']
x = df.drop('salary', axis=1)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# alpha for regression was obtained 
# from plotting alpha/rmse graph

# Lasso Regresion
# alpha = 165
lasso_reg = Lasso(alpha=165)
lasso_score = cross_val_score(lasso_reg, x_train, y_train, cv=10, scoring='neg_mean_squared_error').mean()
rmse_lasso = sqrt(-lasso_score)
lasso_reg.fit(x_train, y_train)
lasso_pred = lasso_reg.predict(x_test)
rmse_lasso_pred = sqrt(mean_squared_error(y_test, lasso_pred))
print('Lasso. Train: {}; Predict: {}'.format(rmse_lasso, rmse_lasso_pred))


# Ridge Regression
# alpa = 18
ridge_reg = Ridge(alpha=18)
ridge_score = cross_val_score(ridge_reg, x_train, y_train, cv=10, scoring='neg_mean_squared_error').mean()
rmse_ridge = sqrt(-ridge_score)
ridge_reg.fit(x_train, y_train)
ridge_pred = ridge_reg.predict(x_test)
rmse_ridge_pred = sqrt(mean_squared_error(y_test, ridge_pred))
print('Ridge. Train: {}; Predict: {}'.format(rmse_ridge, rmse_ridge_pred))


# Random Forest 
rf_reg = RandomForestRegressor()
rf_parametres = {'n_estimators': range(100, 320, 20),
                 'max_features': ('auto', 'sqrt', 'log2')
                 }
rf_gs = GridSearchCV(rf_reg, rf_parametres, scoring='neg_mean_squared_error', cv=3, n_jobs=3)
rf_gs.fit(x_train, y_train)
rmse_rf = sqrt(-rf_gs.best_score_)
rf_pred = rf_gs.best_estimator_.predict(x_test)
rmse_rf_pred = sqrt(mean_squared_error(y_test, rf_pred))
print('Random Forest. Train: {}; Predict: {}'.format(rmse_rf, rmse_rf_pred))


# Support Vector Regression 
# works best with low gamma/high C
sv_reg = SVR()
sv_parametres = {'C': range(10000, 110000, 10000), 
                 'gamma': [x/10 for x in range(1, 11)],
                 }
sv_gs = GridSearchCV(sv_reg, sv_parametres, scoring='neg_mean_squared_error', cv=3, n_jobs=3)
sv_gs.fit(x_train, y_train)
rmse_sv = sqrt(-sv_gs.best_score_)
sv_pred = sv_gs.best_estimator_.predict(x_test)
rmse_sv_pred = sqrt(mean_squared_error(y_test, sv_pred))
print('Support Vector Regression. Train: {}; Predict: {}'.format(rmse_sv, rmse_sv_pred))


# Gradient Boosting
grad_reg = GradientBoostingRegressor()
grad_parametres = {'max_features': ('auto', 'sqrt', 'log2'), 
                   'learning_rate': [x/20 for x in range(1, 12, 2)],
                   'max_depth': range(5, 45, 10),
                   'n_estimators': range(100, 350, 50),
                   }
grad_gs = GridSearchCV(grad_reg, grad_parametres, scoring='neg_mean_squared_error', cv=3, n_jobs=3)
grad_gs.fit(x_train, y_train)
rmse_grad = sqrt(-grad_gs.best_score_)
grad_pred = grad_gs.best_estimator_.predict(x_test)
rmse_grad_pred = sqrt(mean_squared_error(y_test, grad_pred))
print('Gradient Boosting. Train: {}; Predict: {}'.format(rmse_grad, rmse_grad_pred))


# Gradient Boosting is so far the best
file_name = 'final_model.sav'
joblib.dump(grad_gs.best_estimator_, file_name)










