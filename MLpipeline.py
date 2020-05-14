import pandas as pd
import numpy as np
import geopy.distance
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import mean_squared_error
import pickle
import plotly.graph_objects as go

class prep_data(BaseEstimator, TransformerMixin):
    """
    Custom transformer that recodes and transforms data
    """
    def __init__(self, xlist):
        self.xlist = xlist

    def fit(self, X, y=None):
        return(self)

    def transform(self, X):

        rows_begin = X.shape[0]

        # # Coding some time variables
        X['published_date'] = pd.to_datetime(X.published_date)
        X['month'] = X['published_date'].dt.to_period('M').astype(str)
        X['year'] = X['published_date'].dt.to_period('Y').astype(str)        

        # Seperating the string of facilities into dummies
        dummies = X.facility.str.get_dummies(sep=',')
        X = pd.concat([X, dummies], axis=1)

        # True if only one unit is sold. If multiple units, its probably
        # a new development so pricier. 
        X['one_unit'] = X.no_of_units.value_counts().isna()

        # # Only special price types have a value so the na's are replaced with
        # # the string 'normal'
        X.price_type.fillna('Normal', inplace=True)
        
        # # Calculate distance to centre (St. Stephens Green park)
        stephens_green = (53.3382, -6.2591)
        X["dist_to_centre"] = X.apply(
             lambda x: geopy.distance.distance((x.latitude, x.longitude),
                                               stephens_green).km, axis=1)

        # Select variables
        X = X[self.xlist]
        
        assert X.shape[0] == rows_begin
        
        return(X)

class MLpipeline:
    """
    description
    """

    def __init__(self, data):
        """
        Instantiate class
        """
        self.y = np.log(data.price)
        self.X = data.drop(["price"], axis=1)


    def split_data(self, test_size=0.2):
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(self.X, self.y, 
            test_size=test_size, random_state=42)


    def set_estimator(self, estimator, parametersGrid,
                          xlist, numeric_features, categorical_features):
        self.estimator = estimator
        self.parametersGrid = parametersGrid
        self.xlist = xlist
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features


    def build_preprocessor(self):
        """
        Imputes missing values, one hot encodes categorical variables, 
        scales numerical variables and removes outliers.

        Returns a pipeline for a preprocessor 
        """
        # The preprocessing pipeline will be different for numerical and 
        # categorical variables so these will be split up.

        # # For categorical variables        
        categorical_transformer = Pipeline(steps=[
            # impute with most frequent
            ('imputer', SimpleImputer(strategy='most_frequent')),
            # and one hot encode
            ('onehot', OneHotEncoder(handle_unknown='ignore'))])

        #For numeric variables
        numeric_transformer = Pipeline(steps=[
            # impute with median          
            ('imputer', KNNImputer(n_neighbors=10)),
            # rescale
            ('scaler', StandardScaler())])

        #Combine using columntransformer
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)]) 


    def fit_model(self, cv=3):
        """
        """        
        model = Pipeline([('prep_data', prep_data(self.xlist)),
                          ('preprocessor', self.preprocessor),
                          ('estimator', self.estimator)])

        grid = GridSearchCV(model, self.parametersGrid, cv=cv, n_jobs=-1)

        self.grid_fitted = grid.fit(self.X_train, self.y_train)       


    def evaluate_model(self):
        """

        """

        self.y_pred = self.grid_fitted.predict(self.X_test)

        self.r2 = self.grid_fitted.score(self.X_test, self.y_test)
        self.rmse = np.sqrt(mean_squared_error(self.y_test, self.y_pred))

        print("R squared: {:.4f}".format(self.r2))
        print("RMSE: {:.4f}".format(self.rmse))
        print("Tuned best parameters: {}".format(self.grid_fitted.best_params_))

        import plotly.express as px
        fig = px.scatter(x=self.y_test, y=self.y_pred,
                labels={'x':'Observed',
                        'y': 'Predicted'})
        fig.show()

    def run(self):
        self.split_data()
        self.build_preprocessor()
        self.fit_model()
        self.evaluate_model()


    def save_model(self, model_filepath):
        """Pickles model"""
        with open(model_filepath, 'wb') as file:
            pickle.dump(self.grid_fitted.best_estimator_, file)





