import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error

class PM25Forecaster:
    """
    Class dùng để chuẩn bị dữ liệu và huấn luyện mô hình hồi quy dự báo PM2.5
    """
    def __init__(self, data):
        self.data = data
        self.model = LinearRegression()
        self.metrics = {}

    def create_features(self, lag_hours=[1, 3, 24]):
        """
        Tạo các đặc trưng trễ (Lag features).
        Ví dụ: Lag 1 là giá trị PM2.5 của 1 giờ trước.
        """
        print("Dang tao dac trung (Feature Engineering)...")
        df = self.data.copy()
        
        # Target: PM2.5 ở giờ tiếp theo (t+1) - Đây là cái chúng ta cần dự báo
        df['target'] = df.groupby('station')['PM2.5'].shift(-1)
        
        # Lag features: Dùng quá khứ để đoán tương lai
        for lag in lag_hours:
            df[f'PM2.5_lag_{lag}'] = df.groupby('station')['PM2.5'].shift(lag)
            
        # Thêm thông tin thời gian
        df['hour'] = df['datetime'].dt.hour
        df['month'] = df['datetime'].dt.month
        
        # Xóa các dòng bị thiếu dữ liệu do quá trình shift
        df.dropna(inplace=True)
        return df

    def train_test_split(self, df, cutoff_date='2017-01-01'):
        """
        Chia train/test theo mốc thời gian (Cutoff).
        QUAN TRỌNG: Không được shuffle (xáo trộn) để tránh nhìn thấy tương lai.
        """
        print(f"Chia du lieu voi m cutoff: {cutoff_date}")
        train = df[df['datetime'] < cutoff_date]
        test = df[df['datetime'] >= cutoff_date]
        return train, test

    def train(self, train_df, feature_cols):
        """Huấn luyện mô hình"""
        print(f"Bat dau train voi cac features: {feature_cols}")
        X_train = train_df[feature_cols]
        y_train = train_df['target']
        
        self.model.fit(X_train, y_train)
        print("Da huan luyen xong mô hinh Baseline.")

    def evaluate(self, test_df, feature_cols):
        """Đánh giá mô hình trên tập Test"""
        X_test = test_df[feature_cols]
        y_test = test_df['target']
        
        # Dự báo
        y_pred = self.model.predict(X_test)
        
        # Tính toán sai số
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        
        self.metrics = {'RMSE': rmse, 'MAE': mae}
        print(f"KET QUA DANH GIA: RMSE={rmse:.2f}, MAE={mae:.2f}")
        return y_pred