import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import matplotlib.pyplot as plt

df_ads = pd.read_pickle('df_ads_mapdata.pkl')

#Selecting relevant variables
df_ads = df_ads[['area','property_type','ber_classification','price','bathrooms','beds','dist_to_centre','surface','caferestaurants', 'churches', 'health', 'parks', 'platforms', 'pubs','schools', 'shops', 'sports', 'stations']]

df_ads.describe()
df_ads = df_ads.drop(df_ads[df_ads.bathrooms>=8].index)
df_ads = df_ads.drop(df_ads[df_ads.beds>=10].index)
df_ads = df_ads.drop(df_ads[df_ads.property_type=='site'].index)
df_ads.loc[df_ads['surface'] > 1000, 'surface'] = np.nan
df_ads = df_ads.drop(df_ads[df_ads.dist_to_centre > 30].index)

plt.hist(df_ads.surface, bins = 100)
plt.show()

df_ads['price_sqm'] = np.log(df_ads.price / df_ads.surface)

plt.hist(df_ads.price_sqm, bins = 100)
plt.show()

#Log transforming the price
df_ads['price'] = np.log(df_ads.price)
plt.hist(df_ads.price, bins = 100)
plt.show()

#Drop rows with missing price
df_ads = df_ads.dropna(subset=['price'])

#Setting up categorical transformer
categorical_features = ['area','property_type','ber_classification']
numeric_features = list(df_ads.columns)
for x in categorical_features:
    numeric_features.remove(x)
numeric_features.remove('price')
numeric_features.remove('price_sqm')
#numeric_features.remove('surface')

# Categorical varibales are imputed with a 'missing' constant and dummies are created
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

# Transform numerical columns by imputing missing values and standardisation
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer()),
    ('scaler', StandardScaler())])

# combining both pipes
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

steps = [('preprocessor', preprocessor),
         ('reg', LinearRegression())]

pipeline = Pipeline(steps)

#parametersGrid = {"preprocessor__num__imputer__strategy": ['mean','median'],
#                  "reg__alpha": np.linspace(0.00001, 10, 5),
#                  "reg__l1_ratio": np.linspace(0.00001, 1, 5)}
parametersGrid = {"preprocessor__num__imputer__strategy": ['mean','median']}

#df_ads = df_ads.dropna(subset=['price_sqm'])
y = df_ads['price']
X = df_ads.drop(['price','price_sqm'], axis=1)
#X = df_ads.drop('surface', axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

reg_cv = GridSearchCV(pipeline, parametersGrid, cv=5)

reg_cv.fit(X_train, y_train)

y_pred = reg_cv.predict(X_test)

r2 = reg_cv.score(X_test,y_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("Tuned best parameters: {}".format(reg_cv.best_params_))
print("Tuned R squared: {}".format(r2))
print("Tuned RMSE: {}".format(rmse))

# Note: ElasticNet shows that the best parameters are an alpha of 0 and an L1 ratio of 0.5, which is the same as linear regresssion
