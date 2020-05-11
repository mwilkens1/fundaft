import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import geopy.distance
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator, TransformerMixin

from sklearn.metrics import mean_squared_error

import seaborn as sns
sns.set()
sns.set_style("white")

class MLpipeline:
    """
    description
    """

    def __init__(self, data):
        """
        Initiates class
        """
        self.data = data #dataframe

    def prep_data(self, xlist):
        """
        Recodes variables, selects variables and seperates y from x
        """

        # Coding some time variables
        self.data['published_date'] = pd.to_datetime(self.data.published_date)
        self.data['month'] = self.data['published_date'].dt.to_period('M') \
                                                        .astype(str)

        # Detecting whether parking is mentioned in the add facility list
        self.data['parking'] = self.data.facility.str.contains('parking', 
                                                case=False, regex=False)
        # Many adds do not have a facility list. Could be that there are
        # facilities but that the list is not filled in. I am assuming there are
        # no facilities.
        self.data.parking.fillna(False, inplace=True)

        # Only special price types have a value so the na's are replaced with
        # the string 'normal'
        self.data.price_type.fillna('Normal', inplace=True)

        # Calculate distance to centre (St. Stephens Green park)
        stephens_green = (53.3382, -6.2591)
        self.data["dist_to_centre"] = self.data.apply(\
            lambda x: geopy.distance.distance((x.latitude, x.longitude),
                                              stephens_green).km, axis=1)
        
        # Dropping rows with missing price
        self.data = self.data.dropna(subset=['price'])

        # Select variables and print info
        self.data = self.data[["price"] + xlist]
        print(self.data.info())
        
        # Seperate into X and y
        # Taking the log price because of the skewed disribution      
        self.y = np.log(self.data.price)
        self.X = self.data.drop(["price"], axis=1)     
        

    def build_preprocessor(self, X_train):
        """
        Imputes missing values, one hot encodes categorical variables, 
        scales numerical variables and removes outliers.

        Returns a pipeline for a preprocessor 
        """
        
        self.X_train = X_train

        # The preprocessing pipeline will be different for numerical and 
        # categorical variables so these will be split up. To do that we need
        # to have the names of each.

        # Get list of categorical features
        categorical_features = self.X_train.columns[
            self.X_train.dtypes == object].tolist()

        # Get list of numeric features
        numeric_features = list(self.X_train.columns)

        for x in categorical_features:
            numeric_features.remove(x)

        #Setting up the preprocessing pipeline

        # For categorical variables...        
        categorical_transformer = Pipeline(steps=[
            # impute with most frequent
            ('imputer', SimpleImputer(strategy='most_frequent')),
            # and one hot encode
            ('onehot', OneHotEncoder(handle_unknown='ignore'))])

        #For numeric variables ...
        numeric_transformer = Pipeline(steps=[
            # impute with median
            ('imputer', SimpleImputer(strategy='median')),
            # rescale
            ('scaler', StandardScaler())])

        #Combine using columntransformer
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)])   

    def fit_model(self, y_train, estimator, parametersGrid):
        """
        """
        
        model = Pipeline([('preprocessor', self.preprocessor),
                          ('estimator', estimator)])

        grid = GridSearchCV(model, parametersGrid, cv=3, n_jobs=-1)

        self.grid_fitted = grid.fit(self.X_train, y_train)       

    def evaluate_model(self, X_test, y_test):
        """

        """

        y_pred = self.grid_fitted.predict(X_test)

        r2 = self.grid_fitted.score(X_test, y_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        print("R squared: {:.4f}".format(r2))
        print("RMSE: {:.4f}".format(rmse))
        print("Tuned best parameters: {}".format(self.grid_fitted.best_params_))

        sns.distplot(y_test, hist=False, kde=True,
                    kde_kws={'shade': True, 'linewidth': 3},
                    label="Test set")
        sns.distplot(y_pred, hist=False, kde=True,
                    kde_kws={'shade': True, 'linewidth': 3},
                    label="Predicted")
        plt.xlabel("log(price)")
        plt.title("Prediction v test")        
        plt.tight_layout()
        plt.show()

    def save_model(self):
        pass




