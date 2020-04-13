import pandas as pd
import numpy as np
import geopy.distance
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.ensemble import IsolationForest

class MLpipeline:
    """
    description
    """

    def __init__(self, data, xlist):
        """Initiates class, recodes variables, selects variables 
        and seperates y from x"""

        self.data = data #dataframe

        # Recodes
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


    def split_data(self, test_size=0.2, random_state=42):
        """Splits data into training and testing sets"""

        self.X_train, self.X_test, self.y_train, self.y_test = \
        train_test_split(self.X, self.y, 
                        test_size=test_size, random_state=random_state)
        
        print("Rows in training data: {}".format(len(self.X_train)))
        print("Rows in testing data: {}".format(len(self.X_test)))

    
    def build_model(self):
        """

        1. Outlier removal
        2. Imputation
        3. Rescaling / one hot encoding

        """
        
        # The preprocessing pipeline will be different for numerical and 
        # categorical variables so these will be split up. To do that we need
        # to have the names of each.

        # Get list of categorical features
        categorical_features = self.X_train.columns[ \
            self.X_train.dtypes == object].tolist()

        # Get list of numeric features
        numeric_features = list(self.X_train.columns)

        for x in categorical_features:
            numeric_features.remove(x)        
        



    def evaluate_model(self):
        pass

    def save_model(self):
        pass


    

